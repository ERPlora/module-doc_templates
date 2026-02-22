"""
Integration tests for Document Templates views.
"""

import json
import uuid
import pytest
from django.test import Client
from django.urls import reverse


pytestmark = [pytest.mark.django_db, pytest.mark.unit]


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class TestDashboard:

    def test_requires_login(self):
        client = Client()
        response = client.get('/m/doc_templates/')
        assert response.status_code == 302

    def test_dashboard_loads(self, auth_client):
        response = auth_client.get('/m/doc_templates/')
        assert response.status_code == 200

    def test_htmx_returns_partial(self, auth_client):
        response = auth_client.get('/m/doc_templates/', HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_dashboard_with_templates(self, auth_client, receipt_template, invoice_template):
        response = auth_client.get('/m/doc_templates/')
        assert response.status_code == 200

    def test_dashboard_empty(self, auth_client):
        response = auth_client.get('/m/doc_templates/')
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Template Create
# ---------------------------------------------------------------------------

class TestTemplateCreate:

    def test_create_form_loads(self, auth_client):
        response = auth_client.get('/m/doc_templates/create/')
        assert response.status_code == 200

    def test_create_template_success(self, auth_client):
        from doc_templates.models import DocumentTemplate
        response = auth_client.post('/m/doc_templates/create/', {
            'name': 'Test Receipt',
            'doc_type': 'receipt',
            'paper_size': 'thermal_80mm',
            'content': 'Receipt #{{sale.number}} Total: {{sale.total}}',
            'header_content': '',
            'footer_content': '',
            'css_styles': '',
            'is_active': True,
        })
        assert response.status_code == 200
        assert DocumentTemplate.objects.filter(name='Test Receipt').exists()

    def test_create_template_missing_name(self, auth_client):
        from doc_templates.models import DocumentTemplate
        response = auth_client.post('/m/doc_templates/create/', {
            'name': '',
            'doc_type': 'receipt',
            'paper_size': 'thermal_80mm',
            'content': 'Test content',
        })
        assert response.status_code == 200
        # Form should show errors but not crash
        assert not DocumentTemplate.objects.filter(content='Test content').exists()


# ---------------------------------------------------------------------------
# Template Edit
# ---------------------------------------------------------------------------

class TestTemplateEdit:

    def test_edit_form_loads(self, auth_client, receipt_template):
        response = auth_client.get(f'/m/doc_templates/{receipt_template.pk}/edit/')
        assert response.status_code == 200

    def test_edit_template_success(self, auth_client, receipt_template):
        response = auth_client.post(f'/m/doc_templates/{receipt_template.pk}/edit/', {
            'name': 'Updated Receipt',
            'doc_type': 'receipt',
            'paper_size': 'thermal_80mm',
            'content': 'Updated content {{sale.total}}',
            'header_content': '',
            'footer_content': '',
            'css_styles': '',
            'is_active': True,
        })
        assert response.status_code == 200
        receipt_template.refresh_from_db()
        assert receipt_template.name == 'Updated Receipt'
        assert receipt_template.version == 2  # version incremented

    def test_edit_not_found(self, auth_client):
        fake_uuid = uuid.uuid4()
        response = auth_client.get(f'/m/doc_templates/{fake_uuid}/edit/')
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Template Delete
# ---------------------------------------------------------------------------

class TestTemplateDelete:

    def test_delete_template(self, auth_client, receipt_template):
        response = auth_client.post(f'/m/doc_templates/{receipt_template.pk}/delete/')
        data = response.json()
        assert data['success'] is True
        receipt_template.refresh_from_db()
        assert receipt_template.is_deleted is True

    def test_delete_not_found(self, auth_client):
        fake_uuid = uuid.uuid4()
        response = auth_client.post(f'/m/doc_templates/{fake_uuid}/delete/')
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Template Duplicate
# ---------------------------------------------------------------------------

class TestTemplateDuplicate:

    def test_duplicate_template(self, auth_client, receipt_template):
        from doc_templates.models import DocumentTemplate
        response = auth_client.post(f'/m/doc_templates/{receipt_template.pk}/duplicate/')
        data = response.json()
        assert data['success'] is True
        assert 'template_id' in data
        assert 'Copy' in data['name']

        # Verify duplicate exists and is not default
        new_tpl = DocumentTemplate.objects.get(pk=data['template_id'])
        assert new_tpl.is_default is False
        assert new_tpl.content == receipt_template.content

    def test_duplicate_not_found(self, auth_client):
        fake_uuid = uuid.uuid4()
        response = auth_client.post(f'/m/doc_templates/{fake_uuid}/duplicate/')
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Template Preview
# ---------------------------------------------------------------------------

class TestTemplatePreview:

    def test_preview_loads(self, auth_client, receipt_template):
        response = auth_client.get(f'/m/doc_templates/{receipt_template.pk}/preview/')
        assert response.status_code == 200

    def test_preview_not_found(self, auth_client):
        fake_uuid = uuid.uuid4()
        response = auth_client.get(f'/m/doc_templates/{fake_uuid}/preview/')
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Template Set Default
# ---------------------------------------------------------------------------

class TestTemplateSetDefault:

    def test_set_default(self, auth_client, hub_id):
        from doc_templates.models import DocumentTemplate
        tpl1 = DocumentTemplate.objects.create(
            hub_id=hub_id, name='Tpl 1', doc_type='receipt',
            content='Content 1', is_default=True,
        )
        tpl2 = DocumentTemplate.objects.create(
            hub_id=hub_id, name='Tpl 2', doc_type='receipt',
            content='Content 2', is_default=False,
        )

        response = auth_client.post(f'/m/doc_templates/{tpl2.pk}/set-default/')
        data = response.json()
        assert data['success'] is True

        tpl1.refresh_from_db()
        tpl2.refresh_from_db()
        assert tpl1.is_default is False
        assert tpl2.is_default is True


# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

class TestVariablesView:

    def test_variables_loads(self, auth_client):
        response = auth_client.get('/m/doc_templates/variables/')
        assert response.status_code == 200

    def test_variables_with_data(self, auth_client, system_variable, custom_variable):
        response = auth_client.get('/m/doc_templates/variables/')
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Variable Create
# ---------------------------------------------------------------------------

class TestVariableCreate:

    def test_create_form_get(self, auth_client):
        response = auth_client.get('/m/doc_templates/variables/create/')
        assert response.status_code == 200

    def test_create_variable_success(self, auth_client):
        from doc_templates.models import TemplateVariable
        response = auth_client.post('/m/doc_templates/variables/create/', {
            'name': 'custom.new_var',
            'description': 'A new custom variable',
            'variable_group': 'custom',
            'data_type': 'text',
            'example_value': 'Hello',
        })
        data = response.json()
        assert data['success'] is True
        var = TemplateVariable.objects.get(name='custom.new_var')
        assert var.is_system is False

    def test_create_variable_missing_name(self, auth_client):
        response = auth_client.post('/m/doc_templates/variables/create/', {
            'name': '',
            'variable_group': 'custom',
            'data_type': 'text',
        })
        data = response.json()
        assert data['success'] is False


# ---------------------------------------------------------------------------
# Variable Delete
# ---------------------------------------------------------------------------

class TestVariableDelete:

    def test_delete_custom_variable(self, auth_client, custom_variable):
        response = auth_client.post(f'/m/doc_templates/variables/{custom_variable.pk}/delete/')
        data = response.json()
        assert data['success'] is True
        custom_variable.refresh_from_db()
        assert custom_variable.is_deleted is True

    def test_cannot_delete_system_variable(self, auth_client, system_variable):
        response = auth_client.post(f'/m/doc_templates/variables/{system_variable.pk}/delete/')
        data = response.json()
        assert data['success'] is False
        system_variable.refresh_from_db()
        assert system_variable.is_deleted is False

    def test_delete_not_found(self, auth_client):
        fake_uuid = uuid.uuid4()
        response = auth_client.post(f'/m/doc_templates/variables/{fake_uuid}/delete/')
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Render API
# ---------------------------------------------------------------------------

class TestRenderAPI:

    def test_render_success(self, auth_client, receipt_template):
        response = auth_client.post(
            '/m/doc_templates/api/render/',
            data=json.dumps({
                'template_id': str(receipt_template.pk),
                'data': {
                    'sale.number': 'TEST-001',
                    'sale.date': '22/02/2026',
                    'sale.total': '99.99',
                    'customer.name': 'John Doe',
                },
            }),
            content_type='application/json',
        )
        data = response.json()
        assert data['success'] is True
        assert 'TEST-001' in data['html']
        assert '99.99' in data['html']
        assert 'John Doe' in data['html']

    def test_render_with_save(self, auth_client, receipt_template):
        from doc_templates.models import GeneratedDocument
        response = auth_client.post(
            '/m/doc_templates/api/render/',
            data=json.dumps({
                'template_id': str(receipt_template.pk),
                'data': {'sale.number': 'SAVE-001', 'sale.total': '50.00'},
                'save': True,
                'source_id': str(uuid.uuid4()),
            }),
            content_type='application/json',
        )
        data = response.json()
        assert data['success'] is True
        assert GeneratedDocument.objects.filter(doc_type='receipt').exists()

    def test_render_missing_template_id(self, auth_client):
        response = auth_client.post(
            '/m/doc_templates/api/render/',
            data=json.dumps({'data': {}}),
            content_type='application/json',
        )
        data = response.json()
        assert data['success'] is False

    def test_render_invalid_json(self, auth_client):
        response = auth_client.post(
            '/m/doc_templates/api/render/',
            data='not json',
            content_type='application/json',
        )
        data = response.json()
        assert data['success'] is False

    def test_render_template_not_found(self, auth_client):
        response = auth_client.post(
            '/m/doc_templates/api/render/',
            data=json.dumps({
                'template_id': str(uuid.uuid4()),
                'data': {},
            }),
            content_type='application/json',
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class TestSettingsView:

    def test_settings_loads(self, auth_client):
        response = auth_client.get('/m/doc_templates/settings/')
        assert response.status_code == 200

    def test_settings_save(self, auth_client, hub_id, template_settings):
        from doc_templates.models import TemplateSettings
        response = auth_client.post('/m/doc_templates/settings/save/', {
            'default_paper_size': 'a4',
            'default_font_size': '14',
            'company_name': 'Test Corp',
            'company_address': '123 Main St',
            'company_tax_id': 'B12345678',
            'company_phone': '+34 600 000 000',
            'company_email': 'info@testcorp.com',
            'company_website': 'https://testcorp.com',
            'footer_text': 'Thank you for your business',
        })
        data = response.json()
        assert data['success'] is True

        refreshed = TemplateSettings.get_settings(hub_id)
        assert refreshed.default_paper_size == 'a4'
        assert refreshed.default_font_size == 14
        assert refreshed.company_name == 'Test Corp'
        assert refreshed.company_tax_id == 'B12345678'

    def test_settings_requires_login(self):
        client = Client()
        response = client.get('/m/doc_templates/settings/')
        assert response.status_code == 302

    def test_settings_save_requires_login(self):
        client = Client()
        response = client.post('/m/doc_templates/settings/save/', {
            'default_paper_size': 'a4',
            'default_font_size': '12',
        })
        assert response.status_code == 302
