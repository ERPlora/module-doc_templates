import re

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import HubBaseModel


# ---------------------------------------------------------------------------
# Paper Size Choices (shared across models)
# ---------------------------------------------------------------------------

PAPER_SIZE_CHOICES = [
    ('thermal_80mm', _('Thermal 80mm')),
    ('thermal_58mm', _('Thermal 58mm')),
    ('a4', _('A4')),
    ('a5', _('A5')),
    ('letter', _('Letter')),
]


# ---------------------------------------------------------------------------
# Template Settings
# ---------------------------------------------------------------------------

class TemplateSettings(HubBaseModel):
    """Per-hub document template configuration."""

    default_paper_size = models.CharField(
        _('Default Paper Size'),
        max_length=20,
        choices=PAPER_SIZE_CHOICES,
        default='thermal_80mm',
    )
    default_font_size = models.IntegerField(
        _('Default Font Size'),
        default=12,
    )
    company_logo = models.ImageField(
        _('Company Logo'),
        upload_to='doc_templates/logos/',
        null=True,
        blank=True,
    )
    company_name = models.CharField(
        _('Company Name'),
        max_length=255,
        blank=True,
        default='',
    )
    company_address = models.TextField(
        _('Company Address'),
        blank=True,
        default='',
    )
    company_tax_id = models.CharField(
        _('Tax ID'),
        max_length=50,
        blank=True,
        default='',
    )
    company_phone = models.CharField(
        _('Phone'),
        max_length=20,
        blank=True,
        default='',
    )
    company_email = models.EmailField(
        _('Email'),
        blank=True,
        default='',
    )
    company_website = models.URLField(
        _('Website'),
        blank=True,
        default='',
    )
    footer_text = models.TextField(
        _('Footer Text'),
        blank=True,
        default='',
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'doc_templates_settings'
        verbose_name = _('Template Settings')
        verbose_name_plural = _('Template Settings')
        unique_together = [('hub_id',)]

    def __str__(self):
        return f"Template Settings (hub {self.hub_id})"

    @classmethod
    def get_settings(cls, hub_id):
        """Get or create settings for a hub."""
        settings, _ = cls.all_objects.get_or_create(hub_id=hub_id)
        return settings


# ---------------------------------------------------------------------------
# Document Template
# ---------------------------------------------------------------------------

DOC_TYPE_CHOICES = [
    ('receipt', _('Receipt')),
    ('invoice', _('Invoice')),
    ('quote', _('Quote')),
    ('credit_note', _('Credit Note')),
    ('delivery_note', _('Delivery Note')),
    ('custom', _('Custom')),
]


class DocumentTemplate(HubBaseModel):
    """Template definition for documents."""

    name = models.CharField(
        _('Name'),
        max_length=200,
    )
    doc_type = models.CharField(
        _('Document Type'),
        max_length=20,
        choices=DOC_TYPE_CHOICES,
        default='receipt',
    )
    paper_size = models.CharField(
        _('Paper Size'),
        max_length=20,
        choices=PAPER_SIZE_CHOICES,
        default='thermal_80mm',
    )
    content = models.TextField(
        _('Content'),
        help_text=_('Template content with variable placeholders {{variable}}'),
    )
    header_content = models.TextField(
        _('Header Content'),
        blank=True,
        default='',
    )
    footer_content = models.TextField(
        _('Footer Content'),
        blank=True,
        default='',
    )
    css_styles = models.TextField(
        _('CSS Styles'),
        blank=True,
        default='',
        help_text=_('Custom CSS for this template'),
    )
    is_default = models.BooleanField(
        _('Is Default'),
        default=False,
    )
    is_active = models.BooleanField(
        _('Active'),
        default=True,
    )
    version = models.PositiveIntegerField(
        _('Version'),
        default=1,
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'doc_templates_template'
        verbose_name = _('Document Template')
        verbose_name_plural = _('Document Templates')
        ordering = ['doc_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_doc_type_display()})"

    def render(self, context_data):
        """
        Render the template with variable substitution.

        Replaces {{variable}} placeholders with values from context_data.
        """
        rendered = self.content

        if context_data:
            for key, value in context_data.items():
                placeholder = '{{' + key + '}}'
                rendered = rendered.replace(placeholder, str(value) if value is not None else '')

        # Remove any unreplaced placeholders
        rendered = re.sub(r'\{\{[^}]+\}\}', '', rendered)

        return rendered

    def save(self, *args, **kwargs):
        """Ensure only one default per doc_type per hub."""
        if self.is_default:
            # Unset other defaults for the same doc_type in this hub
            DocumentTemplate.objects.filter(
                hub_id=self.hub_id,
                doc_type=self.doc_type,
                is_default=True,
            ).exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Template Variable
# ---------------------------------------------------------------------------

VARIABLE_GROUP_CHOICES = [
    ('sale', _('Sale')),
    ('invoice', _('Invoice')),
    ('customer', _('Customer')),
    ('product', _('Product')),
    ('company', _('Company')),
    ('custom', _('Custom')),
]

DATA_TYPE_CHOICES = [
    ('text', _('Text')),
    ('number', _('Number')),
    ('date', _('Date')),
    ('currency', _('Currency')),
    ('image', _('Image')),
    ('list', _('List')),
]


class TemplateVariable(HubBaseModel):
    """Available variables for document templates."""

    name = models.CharField(
        _('Name'),
        max_length=100,
        help_text=_('Variable name e.g. {{sale.total}}'),
    )
    description = models.TextField(
        _('Description'),
        blank=True,
        default='',
    )
    variable_group = models.CharField(
        _('Group'),
        max_length=20,
        choices=VARIABLE_GROUP_CHOICES,
        default='custom',
    )
    data_type = models.CharField(
        _('Data Type'),
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        default='text',
    )
    example_value = models.CharField(
        _('Example Value'),
        max_length=255,
        blank=True,
        default='',
    )
    is_system = models.BooleanField(
        _('System Variable'),
        default=True,
        help_text=_('System variables cannot be deleted'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'doc_templates_variable'
        verbose_name = _('Template Variable')
        verbose_name_plural = _('Template Variables')
        ordering = ['variable_group', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_variable_group_display()})"


# ---------------------------------------------------------------------------
# Generated Document
# ---------------------------------------------------------------------------

class GeneratedDocument(HubBaseModel):
    """Record of generated documents."""

    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_documents',
        verbose_name=_('Template'),
    )
    doc_type = models.CharField(
        _('Document Type'),
        max_length=50,
    )
    source_id = models.UUIDField(
        _('Source ID'),
        null=True,
        blank=True,
        help_text=_('ID of the source object (sale, invoice, etc.)'),
    )
    rendered_content = models.TextField(
        _('Rendered Content'),
    )
    file = models.FileField(
        _('File'),
        upload_to='doc_templates/generated/',
        null=True,
        blank=True,
    )
    generated_at = models.DateTimeField(
        _('Generated At'),
        auto_now_add=True,
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'doc_templates_generated'
        verbose_name = _('Generated Document')
        verbose_name_plural = _('Generated Documents')
        ordering = ['-generated_at']

    def __str__(self):
        tpl_name = self.template.name if self.template else _('Deleted Template')
        return f"{tpl_name} - {self.doc_type} ({self.generated_at})"
