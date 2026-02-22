import json
import uuid

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from apps.accounts.decorators import login_required
from apps.core.htmx import htmx_view
from apps.modules_runtime.navigation import with_module_nav

from .models import (
    DocumentTemplate, TemplateVariable, TemplateSettings, GeneratedDocument,
)
from .forms import DocumentTemplateForm, TemplateVariableForm, TemplateSettingsForm


def _hub_id(request):
    return request.session.get('hub_id')


# ============================================================================
# Dashboard - Template list
# ============================================================================

@require_http_methods(["GET"])
@login_required
@with_module_nav('doc_templates', 'dashboard')
@htmx_view('doc_templates/pages/dashboard.html', 'doc_templates/partials/dashboard_content.html')
def dashboard(request):
    """List all templates grouped by doc_type."""
    hub = _hub_id(request)
    templates = DocumentTemplate.objects.filter(
        hub_id=hub, is_deleted=False,
    ).order_by('doc_type', 'name')

    # Group templates by doc_type
    grouped = {}
    for tpl in templates:
        doc_type = tpl.get_doc_type_display()
        if doc_type not in grouped:
            grouped[doc_type] = []
        grouped[doc_type].append(tpl)

    total_count = templates.count()
    active_count = templates.filter(is_active=True).count()

    return {
        'grouped_templates': grouped,
        'total_count': total_count,
        'active_count': active_count,
    }


# ============================================================================
# Template CRUD
# ============================================================================

@require_http_methods(["GET", "POST"])
@login_required
@with_module_nav('doc_templates', 'dashboard')
@htmx_view('doc_templates/pages/template_form.html', 'doc_templates/partials/template_form_content.html')
def template_create(request):
    """Create a new document template."""
    hub = _hub_id(request)

    if request.method == 'POST':
        form = DocumentTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.hub_id = hub
            template.save()
            return {
                'form': DocumentTemplateForm(),
                'success': True,
                'message': _('Template created successfully'),
                'template': template,
            }
        return {'form': form}

    return {'form': DocumentTemplateForm()}


@require_http_methods(["GET", "POST"])
@login_required
@with_module_nav('doc_templates', 'dashboard')
@htmx_view('doc_templates/pages/template_form.html', 'doc_templates/partials/template_form_content.html')
def template_edit(request, pk):
    """Edit an existing document template."""
    hub = _hub_id(request)
    template = get_object_or_404(
        DocumentTemplate, pk=pk, hub_id=hub, is_deleted=False,
    )

    if request.method == 'POST':
        form = DocumentTemplateForm(request.POST, instance=template)
        if form.is_valid():
            template = form.save(commit=False)
            template.version += 1
            template.save()
            return {
                'form': form,
                'template': template,
                'success': True,
                'message': _('Template updated successfully'),
                'editing': True,
            }
        return {'form': form, 'template': template, 'editing': True}

    form = DocumentTemplateForm(instance=template)

    # Sample data for live preview
    sample_data = _get_sample_data()

    return {
        'form': form,
        'template': template,
        'editing': True,
        'sample_data': sample_data,
    }


@require_http_methods(["POST"])
@login_required
def template_delete(request, pk):
    """Soft delete a template."""
    hub = _hub_id(request)

    template = get_object_or_404(
        DocumentTemplate, pk=pk, hub_id=hub, is_deleted=False,
    )
    try:
        template.is_deleted = True
        template.deleted_at = timezone.now()
        template.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
@login_required
def template_duplicate(request, pk):
    """Duplicate an existing template."""
    hub = _hub_id(request)

    original = get_object_or_404(
        DocumentTemplate, pk=pk, hub_id=hub, is_deleted=False,
    )
    try:
        new_template = DocumentTemplate.objects.create(
            hub_id=hub,
            name=f"{original.name} ({_('Copy')})",
            doc_type=original.doc_type,
            paper_size=original.paper_size,
            content=original.content,
            header_content=original.header_content,
            footer_content=original.footer_content,
            css_styles=original.css_styles,
            is_default=False,
            is_active=True,
            version=1,
        )

        return JsonResponse({
            'success': True,
            'template_id': str(new_template.pk),
            'name': new_template.name,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
@login_required
def template_preview(request, pk):
    """Render a template with sample data."""
    hub = _hub_id(request)
    template = get_object_or_404(
        DocumentTemplate, pk=pk, hub_id=hub, is_deleted=False,
    )

    sample_data = _get_sample_data()
    rendered = template.render(sample_data)

    return render(request, 'doc_templates/partials/preview.html', {
        'template': template,
        'rendered_content': rendered,
        'sample_data': sample_data,
    })


@require_http_methods(["POST"])
@login_required
def template_set_default(request, pk):
    """Set a template as the default for its doc_type."""
    hub = _hub_id(request)

    try:
        template = get_object_or_404(
            DocumentTemplate, pk=pk, hub_id=hub, is_deleted=False,
        )
        template.is_default = True
        template.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================================================
# Variables
# ============================================================================

@require_http_methods(["GET"])
@login_required
@with_module_nav('doc_templates', 'variables')
@htmx_view('doc_templates/pages/variables.html', 'doc_templates/partials/variables_content.html')
def variables(request):
    """List all available template variables."""
    hub = _hub_id(request)
    all_variables = TemplateVariable.objects.filter(
        hub_id=hub, is_deleted=False,
    ).order_by('variable_group', 'name')

    # Group by variable_group
    grouped = {}
    for var in all_variables:
        group = var.get_variable_group_display()
        if group not in grouped:
            grouped[group] = []
        grouped[group].append(var)

    form = TemplateVariableForm()

    return {
        'grouped_variables': grouped,
        'variables_list': all_variables,
        'form': form,
    }


@require_http_methods(["GET", "POST"])
@login_required
def variable_create(request):
    """Create a custom template variable."""
    hub = _hub_id(request)

    if request.method == 'POST':
        form = TemplateVariableForm(request.POST)
        if form.is_valid():
            variable = form.save(commit=False)
            variable.hub_id = hub
            variable.is_system = False
            variable.save()
            return JsonResponse({
                'success': True,
                'variable_id': str(variable.pk),
                'name': variable.name,
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors,
        }, status=400)

    form = TemplateVariableForm()
    return render(request, 'doc_templates/partials/variable_form.html', {
        'form': form,
    })


@require_http_methods(["POST"])
@login_required
def variable_delete(request, pk):
    """Delete a custom variable (system variables cannot be deleted)."""
    hub = _hub_id(request)

    variable = get_object_or_404(
        TemplateVariable, pk=pk, hub_id=hub, is_deleted=False,
    )
    try:
        if variable.is_system:
            return JsonResponse({
                'success': False,
                'error': str(_('System variables cannot be deleted')),
            }, status=400)

        variable.is_deleted = True
        variable.deleted_at = timezone.now()
        variable.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================================================
# Render API
# ============================================================================

@require_http_methods(["POST"])
@login_required
def api_render(request):
    """API endpoint to render a template with provided data. Returns HTML."""
    hub = _hub_id(request)

    try:
        body = json.loads(request.body)
        template_id = body.get('template_id')
        context_data = body.get('data', {})
        source_id = body.get('source_id')

        if not template_id:
            return JsonResponse({
                'success': False,
                'error': str(_('template_id is required')),
            }, status=400)

        template = get_object_or_404(
            DocumentTemplate, pk=template_id, hub_id=hub, is_deleted=False,
        )

        rendered = template.render(context_data)

        # Optionally save the generated document
        if body.get('save', False):
            source_uuid = None
            if source_id:
                try:
                    source_uuid = uuid.UUID(str(source_id))
                except (ValueError, AttributeError):
                    pass

            GeneratedDocument.objects.create(
                hub_id=hub,
                template=template,
                doc_type=template.doc_type,
                source_id=source_uuid,
                rendered_content=rendered,
            )

        return JsonResponse({
            'success': True,
            'html': rendered,
            'template_name': template.name,
            'doc_type': template.doc_type,
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': str(_('Invalid JSON body')),
        }, status=400)
    except Http404:
        raise
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================================================
# Settings
# ============================================================================

@require_http_methods(["GET"])
@login_required
@with_module_nav('doc_templates', 'settings')
@htmx_view('doc_templates/pages/settings.html', 'doc_templates/partials/settings_content.html')
def settings_view(request):
    """Display template settings."""
    hub = _hub_id(request)
    settings = TemplateSettings.get_settings(hub)
    form = TemplateSettingsForm(instance=settings)

    return {
        'settings': settings,
        'settings_form': form,
    }


@require_http_methods(["POST"])
@login_required
def settings_save(request):
    """Save template settings."""
    hub = _hub_id(request)

    try:
        settings = TemplateSettings.get_settings(hub)
        form = TemplateSettingsForm(request.POST, request.FILES, instance=settings)

        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})

        return JsonResponse({
            'success': False,
            'errors': form.errors,
        }, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============================================================================
# Helpers
# ============================================================================

def _get_sample_data():
    """Return sample data for template preview."""
    return {
        'company.name': 'ERPlora Demo',
        'company.address': '123 Main Street, City',
        'company.phone': '+34 612 345 678',
        'company.tax_id': 'B12345678',
        'company.email': 'info@erplora.com',
        'company.website': 'https://erplora.com',
        'sale.number': '20260222-0001',
        'sale.date': '22/02/2026',
        'sale.time': '14:30',
        'sale.subtotal': '82.64',
        'sale.tax': '17.36',
        'sale.total': '100.00',
        'sale.payment_method': 'Cash',
        'sale.employee': 'John Doe',
        'sale.items': '1x Product A - 50.00\n2x Service B - 25.00',
        'customer.name': 'Jane Smith',
        'customer.email': 'jane@example.com',
        'customer.phone': '+34 600 123 456',
        'invoice.number': 'INV-2026-0001',
        'invoice.date': '22/02/2026',
        'invoice.due_date': '22/03/2026',
    }
