from urllib.parse import urlencode

from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils.html import format_html
import swapper

ReportDefinition = swapper.load_model("template_reports", "ReportDefinition")
ReportRun = swapper.load_model("template_reports", "ReportRun")


class ChooseReportDefinitionForm(forms.Form):
    """
    Lets an admin pick a ReportDefinition via a Select2 autocomplete
    instead of a giant <select>.  We reuse the FK on ReportRun so we
    don't have to invent a dummy model just for the widget.
    """

    report_definition = forms.ModelChoiceField(
        queryset=ReportDefinition.objects.none(),  # filled in __init__
        label="Report Template",
    )

    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model", None)
        super().__init__(*args, **kwargs)

        # Filter down to ReportDefinitions allowed for this model.
        field = self.fields["report_definition"]
        field.queryset = ReportDefinition.filter_for_allowed_models(model)

        # HACK:
        # AutocompleteSelect needs a ForeignKey instance to discover the
        # autocomplete endpoint.  We just hijack the FK that already
        # exists on ReportRun.
        fk = ReportRun._meta.get_field("report_definition")
        widget = admin.widgets.AutocompleteSelect(fk, admin.site)
        widget.choices = field.choices
        field.widget = widget


# This form will be built dynamically based on the ReportDefinition.
# The ReportDefinition is expected to have a method get_required_context_fields()
# that returns a tuple: (fixed_field_name, [other_field_names])
class ConfigureReportContextForm(forms.Form):
    # The fixed_field (e.g. "program") will be displayed as disabled.
    def __init__(self, *args, **kwargs):
        fixed_field = kwargs.pop("fixed_field", None)  # e.g. "program"
        extra_simple_fields = kwargs.pop(
            "extra_simple_fields", []
        )  # e.g. ["constant_name"]

        fixed_queryset = kwargs.pop(
            "fixed_queryset", None
        )  # The queryset from the changelist filter

        super().__init__(*args, **kwargs)

        # For the fixed field, we show a read-only summary (e.g. the number of records, or the filter value)
        if fixed_field:
            self.fields[fixed_field] = forms.CharField(
                label=fixed_field.capitalize(),
                initial=f"{fixed_queryset.count()} records",
                disabled=True,
            )

        # For each additional field, add a text input.
        for field in extra_simple_fields:
            self.fields[field] = forms.CharField(label=field.capitalize(), required=False)


class ReportGenerationAdminMixin(admin.ModelAdmin):
    change_list_template = "admin/report_generation_changelist.html"

    @property
    def choose_report_definition_url_name(self):
        return f"{self.model._meta.app_label}_{self.model._meta.model_name}_choose_report_definition"

    @property
    def configure_report_context_url_name(self):
        return f"{self.model._meta.app_label}_{self.model._meta.model_name}_configure_report_context"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "generate_reports/choose/",
                self.admin_site.admin_view(self.choose_report_definition_view),
                name=self.choose_report_definition_url_name,
            ),
            path(
                "generate_reports/configure/",
                self.admin_site.admin_view(self.configure_report_context_view),
                name=self.configure_report_context_url_name,
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        # Pass the full URL into the context.
        extra_context["choose_report_definition_url"] = reverse(
            f"admin:{self.choose_report_definition_url_name}"
        )

        return super().changelist_view(request, extra_context=extra_context)

    def choose_report_definition_view(self, request):
        """
        Step 1: Display a form to choose a ReportDefinition.
        The current filter (GET parameters) is preserved in the URL.
        """
        # Preserve all GET parameters (i.e. the list filter).
        filter_params = request.GET.dict()
        if request.method == "POST":
            form = ChooseReportDefinitionForm(request.POST, model=self.model)
            if form.is_valid():
                report_def = form.cleaned_data["report_definition"]
                # Redirect to the configure context view, passing the report_def id and filter params.
                params = {"report_def": report_def.pk}
                params.update(filter_params)
                url = reverse(f"admin:{self.configure_report_context_url_name}")
                return HttpResponseRedirect(f"{url}?{urlencode(params)}")
        else:
            form = ChooseReportDefinitionForm(model=self.model)
        context = {
            "form": form,
            "title": "Choose Report Template",
        }
        return render(request, "admin/choose_report_definition.html", context)

    def configure_report_context_view(self, request):
        """
        Step 2: Display a form to configure additional context for the report.
        The fixed queryset is determined by applying the current filter parameters to the model.
        The report definition's required context fields are obtained via a placeholder method.
        """
        # Extract the filter parameters from GET (all except "report_def").
        report_def_id = request.GET.get("report_def")
        if not report_def_id:
            self.message_user(
                request, "No report template selected.", level=messages.ERROR
            )
            return self.redirect_back_to_changelist(request)

        # Build filter parameters for the queryset: use all GET parameters except report_def.
        filter_params = request.GET.copy()
        filter_params.pop("report_def", None)
        # Extract search term 'q'
        q = filter_params.pop("q", [""])[0]
        # Build a base queryset from the remaining GET parameters.
        qs = self.model.objects.filter(**filter_params)
        # Now, if there's a search term, use get_search_results to filter qs.
        if q:
            qs, use_distinct = self.get_search_results(request, qs, q)

        # Fetch the report template and extract its context requirements.
        report_def = ReportDefinition.objects.get(pk=report_def_id)
        context_requirements = report_def.extract_context_requirements()

        # Check that we only have ONE top-level object context key required.
        object_fields_required = context_requirements["object_fields"]
        simple_fields_required = context_requirements["simple_fields"]
        if not object_fields_required:
            self.message_user(
                request,
                f"The report template does not have any top-level object fields, it needs exactly one.",
                level=messages.ERROR,
            )
            return self.redirect_back_to_changelist(request)
        if len(object_fields_required) > 1:
            self.message_user(
                request,
                f"The report template must have exactly one top-level object field among all its "
                f"placeholders, but we found `{object_fields_required}`.",
                level=messages.ERROR,
            )
            return self.redirect_back_to_changelist(request)
        object_key_required = object_fields_required[0]

        # Get defaults for the extra simple fields from the report definition.
        simple_field_defaults = report_def.get_global_context()

        form_kwargs = dict(
            fixed_field=object_key_required,
            extra_simple_fields=simple_fields_required,
            fixed_queryset=qs,
            initial=simple_field_defaults,
        )

        if request.method == "POST":
            form = ConfigureReportContextForm(request.POST, **form_kwargs)
            if form.is_valid():
                additional_context = {}
                for key, value in form.cleaned_data.items():
                    # Skip the fixed field since it's disabled.
                    if key == object_key_required:
                        continue
                    additional_context[key] = value
                # For each record in the filtered queryset, generate a report.
                has_errors = False
                for record in qs:
                    context_data = {object_key_required: record}
                    context_data.update(additional_context)
                    errors = report_def.run_report(
                        context=context_data,
                        perm_user=request.user,
                    )
                    # Errors, break immediately.
                    if errors:
                        for error in errors:
                            self.message_user(
                                request,
                                f"{record} - {error}",
                                level=messages.ERROR,
                            )
                        has_errors = True
                        break
                # Success message
                if not has_errors:
                    runs_changelist_url = reverse(
                        "admin:%s_%s_changelist"
                        % (ReportRun._meta.app_label, ReportRun._meta.model_name)
                    )
                    self.message_user(
                        request,
                        format_html(
                            "Reports generated successfully, see: <a href='{}'>here</a>",
                            runs_changelist_url,
                        ),
                    )
                return self.redirect_back_to_changelist(request)
        else:
            form = ConfigureReportContextForm(**form_kwargs)
        context = {
            "form": form,
            "title": "Configure Report Context",
        }
        return render(request, "admin/configure_report_context.html", context)

    def redirect_back_to_changelist(self, request):
        """
        Redirect back to the changelist view.
        """
        # Redirect (preserve original query parameters except report_def)
        changelist_url = reverse(
            "admin:%s_%s_changelist"
            % (self.model._meta.app_label, self.model._meta.model_name)
        )
        query_params = request.GET.copy()
        query_params.pop("report_def", None)
        if query_params:
            changelist_url = f"{changelist_url}?{urlencode(query_params)}"
        return redirect(changelist_url)
