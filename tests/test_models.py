"""
Unit tests for Document Templates models.
"""

import uuid
import pytest
from django.utils import timezone


pytestmark = [pytest.mark.django_db, pytest.mark.unit]


# ---------------------------------------------------------------------------
# TemplateSettings
# ---------------------------------------------------------------------------

class TestTemplateSettings:
    """Tests for TemplateSettings model."""

    def test_get_settings_creates_singleton(self, hub_id):
        from doc_templates.models import TemplateSettings
        settings = TemplateSettings.get_settings(hub_id)
        assert settings is not None
        assert settings.hub_id == hub_id

    def test_get_settings_returns_existing(self, hub_id):
        from doc_templates.models import TemplateSettings
        s1 = TemplateSettings.get_settings(hub_id)
        s2 = TemplateSettings.get_settings(hub_id)
        assert s1.pk == s2.pk

    def test_default_values(self, template_settings):
        assert template_settings.default_paper_size == 'thermal_80mm'
        assert template_settings.default_font_size == 12
        assert template_settings.company_name == ''
        assert template_settings.company_address == ''
        assert template_settings.company_tax_id == ''
        assert template_settings.company_phone == ''
        assert template_settings.company_email == ''
        assert template_settings.company_website == ''
        assert template_settings.footer_text == ''
        assert not template_settings.company_logo

    def test_str(self, template_settings):
        assert 'Template Settings' in str(template_settings)

    def test_update_settings(self, template_settings):
        from doc_templates.models import TemplateSettings
        template_settings.company_name = 'Test Corp'
        template_settings.company_tax_id = 'B12345678'
        template_settings.default_paper_size = 'a4'
        template_settings.save()

        refreshed = TemplateSettings.get_settings(template_settings.hub_id)
        assert refreshed.company_name == 'Test Corp'
        assert refreshed.company_tax_id == 'B12345678'
        assert refreshed.default_paper_size == 'a4'

    def test_unique_per_hub(self, hub_id, template_settings):
        """Verify unique_together constraint on hub_id."""
        from doc_templates.models import TemplateSettings
        unique = TemplateSettings._meta.unique_together
        assert ('hub_id',) in unique


# ---------------------------------------------------------------------------
# DocumentTemplate
# ---------------------------------------------------------------------------

class TestDocumentTemplate:
    """Tests for DocumentTemplate model."""

    def test_create(self, receipt_template):
        assert receipt_template.name == 'Default Receipt'
        assert receipt_template.doc_type == 'receipt'
        assert receipt_template.paper_size == 'thermal_80mm'
        assert receipt_template.is_default is True
        assert receipt_template.is_active is True
        assert receipt_template.version == 1

    def test_str(self, receipt_template):
        result = str(receipt_template)
        assert 'Default Receipt' in result
        assert 'Receipt' in result

    def test_render_with_variables(self, receipt_template):
        context = {
            'sale.number': '20260222-0001',
            'sale.date': '22/02/2026',
            'sale.total': '100.00',
            'customer.name': 'Jane Smith',
        }
        rendered = receipt_template.render(context)
        assert '20260222-0001' in rendered
        assert '22/02/2026' in rendered
        assert '100.00' in rendered
        assert 'Jane Smith' in rendered

    def test_render_removes_unreplaced_placeholders(self, receipt_template):
        rendered = receipt_template.render({'sale.number': '0001'})
        assert '{{' not in rendered
        assert '}}' not in rendered

    def test_render_with_none_values(self, receipt_template):
        context = {
            'sale.number': None,
            'sale.date': '22/02/2026',
            'sale.total': '50.00',
            'customer.name': 'Test',
        }
        rendered = receipt_template.render(context)
        assert '22/02/2026' in rendered

    def test_render_empty_context(self, receipt_template):
        rendered = receipt_template.render({})
        assert '{{' not in rendered

    def test_render_with_none_context(self, receipt_template):
        rendered = receipt_template.render(None)
        # Should still work, removing unreplaced placeholders
        assert '{{' not in rendered

    def test_default_uniqueness_per_doc_type(self, hub_id, receipt_template):
        """Only one default per doc_type per hub."""
        from doc_templates.models import DocumentTemplate
        assert receipt_template.is_default is True

        # Create another receipt template and set as default
        new_template = DocumentTemplate.objects.create(
            hub_id=hub_id,
            name='New Receipt',
            doc_type='receipt',
            content='New content',
            is_default=True,
        )

        # Original should no longer be default
        receipt_template.refresh_from_db()
        assert receipt_template.is_default is False
        assert new_template.is_default is True

    def test_default_different_doc_types(self, hub_id, receipt_template, invoice_template):
        """Default per doc_type doesn't affect other types."""
        assert receipt_template.is_default is True
        assert invoice_template.is_default is True
        # Both can be default since they're different doc_types

    def test_all_doc_types(self, hub_id):
        from doc_templates.models import DocumentTemplate, DOC_TYPE_CHOICES
        for type_code, _ in DOC_TYPE_CHOICES:
            tpl = DocumentTemplate.objects.create(
                hub_id=hub_id,
                name=f'Template {type_code}',
                doc_type=type_code,
                content=f'Content for {type_code}',
            )
            assert tpl.doc_type == type_code

    def test_all_paper_sizes(self, hub_id):
        from doc_templates.models import DocumentTemplate, PAPER_SIZE_CHOICES
        for size_code, _ in PAPER_SIZE_CHOICES:
            tpl = DocumentTemplate.objects.create(
                hub_id=hub_id,
                name=f'Template {size_code}',
                doc_type='custom',
                content='Test',
                paper_size=size_code,
            )
            assert tpl.paper_size == size_code

    def test_ordering(self, hub_id):
        from doc_templates.models import DocumentTemplate
        tpl_z = DocumentTemplate.objects.create(
            hub_id=hub_id, name='Z Template', doc_type='receipt', content='Z',
        )
        tpl_a = DocumentTemplate.objects.create(
            hub_id=hub_id, name='A Template', doc_type='receipt', content='A',
        )
        templates = list(DocumentTemplate.objects.filter(hub_id=hub_id, doc_type='receipt'))
        names = [t.name for t in templates]
        assert names.index('A Template') < names.index('Z Template')

    def test_soft_delete(self, receipt_template):
        from doc_templates.models import DocumentTemplate
        receipt_template.delete()
        assert receipt_template.is_deleted is True
        assert DocumentTemplate.objects.filter(pk=receipt_template.pk).count() == 0
        assert DocumentTemplate.all_objects.filter(pk=receipt_template.pk).count() == 1

    def test_version_default(self, hub_id):
        from doc_templates.models import DocumentTemplate
        tpl = DocumentTemplate.objects.create(
            hub_id=hub_id, name='Test', doc_type='receipt', content='Test',
        )
        assert tpl.version == 1

    def test_css_styles_optional(self, hub_id):
        from doc_templates.models import DocumentTemplate
        tpl = DocumentTemplate.objects.create(
            hub_id=hub_id, name='No CSS', doc_type='receipt', content='Content',
        )
        assert tpl.css_styles == ''


# ---------------------------------------------------------------------------
# TemplateVariable
# ---------------------------------------------------------------------------

class TestTemplateVariable:
    """Tests for TemplateVariable model."""

    def test_create_system_variable(self, system_variable):
        assert system_variable.name == 'sale.total'
        assert system_variable.variable_group == 'sale'
        assert system_variable.data_type == 'currency'
        assert system_variable.is_system is True

    def test_create_custom_variable(self, custom_variable):
        assert custom_variable.name == 'custom.loyalty_points'
        assert custom_variable.variable_group == 'custom'
        assert custom_variable.is_system is False

    def test_str(self, system_variable):
        result = str(system_variable)
        assert 'sale.total' in result
        assert 'Sale' in result

    def test_all_variable_groups(self, hub_id):
        from doc_templates.models import TemplateVariable, VARIABLE_GROUP_CHOICES
        for group_code, _ in VARIABLE_GROUP_CHOICES:
            var = TemplateVariable.objects.create(
                hub_id=hub_id,
                name=f'{group_code}.test',
                variable_group=group_code,
            )
            assert var.variable_group == group_code

    def test_all_data_types(self, hub_id):
        from doc_templates.models import TemplateVariable, DATA_TYPE_CHOICES
        for type_code, _ in DATA_TYPE_CHOICES:
            var = TemplateVariable.objects.create(
                hub_id=hub_id,
                name=f'test.{type_code}',
                data_type=type_code,
            )
            assert var.data_type == type_code

    def test_ordering(self, hub_id):
        from doc_templates.models import TemplateVariable
        var_z = TemplateVariable.objects.create(
            hub_id=hub_id, name='z_var', variable_group='custom',
        )
        var_a = TemplateVariable.objects.create(
            hub_id=hub_id, name='a_var', variable_group='custom',
        )
        variables = list(TemplateVariable.objects.filter(hub_id=hub_id, variable_group='custom'))
        names = [v.name for v in variables]
        assert names.index('a_var') < names.index('z_var')

    def test_soft_delete(self, custom_variable):
        from doc_templates.models import TemplateVariable
        custom_variable.delete()
        assert custom_variable.is_deleted is True
        assert TemplateVariable.objects.filter(pk=custom_variable.pk).count() == 0
        assert TemplateVariable.all_objects.filter(pk=custom_variable.pk).count() == 1


# ---------------------------------------------------------------------------
# GeneratedDocument
# ---------------------------------------------------------------------------

class TestGeneratedDocument:
    """Tests for GeneratedDocument model."""

    def test_create(self, generated_doc):
        assert generated_doc.doc_type == 'receipt'
        assert generated_doc.rendered_content != ''
        assert generated_doc.source_id is not None
        assert generated_doc.template is not None

    def test_str(self, generated_doc):
        result = str(generated_doc)
        assert 'Default Receipt' in result
        assert 'receipt' in result

    def test_template_set_null_on_delete(self, generated_doc, receipt_template):
        """When template is hard-deleted, FK becomes NULL."""
        receipt_template.delete(hard_delete=True)
        generated_doc.refresh_from_db()
        assert generated_doc.template is None

    def test_ordering_newest_first(self, hub_id, receipt_template):
        from doc_templates.models import GeneratedDocument
        doc1 = GeneratedDocument.objects.create(
            hub_id=hub_id,
            template=receipt_template,
            doc_type='receipt',
            rendered_content='Doc 1',
        )
        doc2 = GeneratedDocument.objects.create(
            hub_id=hub_id,
            template=receipt_template,
            doc_type='receipt',
            rendered_content='Doc 2',
        )
        docs = list(GeneratedDocument.objects.filter(hub_id=hub_id))
        assert docs[0].pk == doc2.pk
        assert docs[1].pk == doc1.pk

    def test_optional_source_id(self, hub_id, receipt_template):
        from doc_templates.models import GeneratedDocument
        doc = GeneratedDocument.objects.create(
            hub_id=hub_id,
            template=receipt_template,
            doc_type='receipt',
            rendered_content='No source',
        )
        assert doc.source_id is None

    def test_optional_file(self, hub_id, receipt_template):
        from doc_templates.models import GeneratedDocument
        doc = GeneratedDocument.objects.create(
            hub_id=hub_id,
            template=receipt_template,
            doc_type='receipt',
            rendered_content='No file',
        )
        assert not doc.file
