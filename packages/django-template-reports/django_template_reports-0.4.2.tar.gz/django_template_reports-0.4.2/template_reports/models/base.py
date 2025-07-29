import datetime
from io import BytesIO
import re
from typing import Any

from django.contrib.auth.models import PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Q
import swapper

from template_reports.office_renderer import (
    render_pptx,
    render_xlsx,
    extract_context_keys,
    identify_file_type,
)
from template_reports.office_renderer.render import render_from_file_stream
from template_reports.templating import process_text

from .utils import get_storage
from template_reports.signals import report_generated


class BaseReportDefinition(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    file = models.FileField(
        upload_to="template_reports/templates/",
        storage=get_storage,
    )

    config = models.JSONField(
        default=dict, blank=True, help_text="Configuration JSON, including allowed models"
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @classmethod
    def filter_for_allowed_models(cls, model):
        """
        Return a queryset of ReportDefinitions that are allowed to run for the given model.
        If no models are provided, return all ReportDefinitions.
        """
        if model:
            full_model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            return cls.objects.filter(
                Q(config__allowed_models__contains=[full_model_name])
                | Q(config__allowed_models=[])
                | Q(config__allowed_models__isnull=True)
            )
        return cls.objects.all()

    def get_file_stream(self):
        self.file.seek(0)
        file_data = self.file.read()
        return BytesIO(file_data)

    def extract_context_requirements(self):
        """
        Analyze the template file and extract the context keys required to render it.
        Return a dict with:
        - simple_fields: sorted list of unique simple keys
        - object_fields: sorted list of unique object keys
        """
        file_stream = self.get_file_stream()
        return extract_context_keys(file_stream)

    def run_report(self, context: dict, perm_user: PermissionsMixin):
        """
        Run the report with the provided context.
        Save the generated report file as ReportRun.
        """

        # Enrich the context with the global context
        global_context = self.get_global_context()
        context = {
            **global_context,
            **context,
        }

        # Render the template file, from the template (turned into a file stream)
        output, errors, file_type = render_from_file_stream(
            template_file_stream=self.get_file_stream(),
            context=context,
            check_permissions=lambda obj: perm_user.has_perm("view", obj),
        )

        # Errors
        if errors:
            return errors

        # Build the filename
        filename = self.build_filename(
            context=context,
            perm_user=perm_user,
            file_type=file_type,
        )

        # Get additional data to save to the report run
        metadata = self.get_extra_creation_kwargs(
            context,
            perm_user,
        )

        # Create a Django ContentFile from the bytes
        # (use the filename method)
        output_content = ContentFile(
            output.getvalue(),
            name=filename,
        )

        # Save the generated report
        ReportRun = swapper.load_model("template_reports", "ReportRun")
        report_run = ReportRun.objects.create(
            report_definition=self,
            file=output_content,
            **metadata,
        )

        # Send signal after report is generated
        report_generated.send(
            sender=self.__class__,
            report_run=report_run,
            context=context,
            perm_user=perm_user,
        )

        # Success
        return None

    def get_global_context(self):
        """
        Return the global context for the report. This can be used to
        provide additional data to the template rendering process.

        Override this if context needs to be pulled from elsewhere too.
        """
        config = self.config or {}
        return config.get("context", {})

    def build_filename(
        self,
        context: dict,
        perm_user: PermissionsMixin,
        file_type: str,
    ) -> str:
        """
        Return the desired name of the template file. Override this method
        to customize the file name.

        The default implementation generates a name based on the current
        timestamp, e.g., "report-20231005123456.pptx".

        If a filename template is provided in the config, it will be used
        to generate the filename. The template can include placeholders
        just like the reports themselves.
        """

        # Check if a filename template is provided in the config
        filename_template = (self.config or {}).get("filename_template", None)
        if filename_template:
            # Add the perm_user to the context
            context = {
                **context,
                "perm_user": perm_user,
            }
            filename = str(
                process_text(
                    text=filename_template,
                    context=context,
                    check_permissions=lambda obj: perm_user.has_perm("view", obj),
                )
            )

        # Default filename generation
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"report-{timestamp}"

        # Ensure the filename ends with extension
        extension = f".{file_type}"
        if not filename.endswith(extension):
            filename += extension

        # Replace certain characters with hyphens, using regex
        filename = re.sub(r"[@&#+\s]", "-", filename)

        return filename

    @classmethod
    def serialize_context_item_value(cls, value):
        """
        Serialize a context item value for storage in the BaseReportRun record.
        """
        # If the value has a primary key, return its string representation.
        if hasattr(value, "pk"):
            return {
                "pk": str(value.pk),
                "str": str(value),
                "model": f"{value._meta.app_label}.{value._meta.model_name}",
            }

        # If the value is a list, serialize each item.
        if isinstance(value, list):
            return [cls.serialize_context_item_value(v) for v in value]

        # If the value is a dict, serialize each key-value pair.
        if isinstance(value, dict):
            return {k: cls.serialize_context_item_value(v) for k, v in value.items()}

        # If the value is a datetime, return its ISO format.
        if isinstance(value, datetime.datetime):
            return value.isoformat()

        # Otherwise, return the string representation of the value.
        return str(value)

    def get_extra_creation_kwargs(
        self,
        context: dict,
        perm_user: PermissionsMixin,
    ) -> dict[str, Any]:
        """
        Return the extra kwargs for a report run with the given context and user.
        Override this method to add more data or metadata.
        """
        return {
            "data": {
                "context": self.serialize_context_item_value(context),
                "perm_user": self.serialize_context_item_value(perm_user),
            }
        }


class BaseReportRun(models.Model):
    report_definition = models.ForeignKey(
        swapper.get_model_name("template_reports", "ReportDefinition"),
        on_delete=models.SET_NULL,
        null=True,
    )

    # We store the run's context and any other metadata in a JSON field.
    data = models.JSONField()

    # The generated PPTX file
    file = models.FileField(
        upload_to="template_reports/generated_reports/",
        storage=get_storage,
    )

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.report_definition.name} run at {self.created}"
