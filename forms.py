from django import forms
from django.utils.translation import gettext_lazy as _

from .models import DocumentTemplate, TemplateVariable, TemplateSettings


class DocumentTemplateForm(forms.ModelForm):
    """Form for creating and editing document templates."""

    class Meta:
        model = DocumentTemplate
        fields = [
            'name', 'doc_type', 'paper_size', 'content',
            'header_content', 'footer_content', 'css_styles',
            'is_default', 'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Template name'),
            }),
            'doc_type': forms.Select(attrs={
                'class': 'select',
            }),
            'paper_size': forms.Select(attrs={
                'class': 'select',
            }),
            'content': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': '15',
                'placeholder': _('Template content with {{variable}} placeholders...'),
            }),
            'header_content': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': '4',
                'placeholder': _('Header content (optional)'),
            }),
            'footer_content': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': '4',
                'placeholder': _('Footer content (optional)'),
            }),
            'css_styles': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': '6',
                'placeholder': _('Custom CSS styles (optional)'),
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
        }


class TemplateVariableForm(forms.ModelForm):
    """Form for creating custom template variables."""

    class Meta:
        model = TemplateVariable
        fields = [
            'name', 'description', 'variable_group',
            'data_type', 'example_value',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('e.g. custom.discount_text'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': '2',
                'placeholder': _('What this variable represents'),
            }),
            'variable_group': forms.Select(attrs={
                'class': 'select',
            }),
            'data_type': forms.Select(attrs={
                'class': 'select',
            }),
            'example_value': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Example: 10% off'),
            }),
        }


class TemplateSettingsForm(forms.ModelForm):
    """Form for template module settings."""

    class Meta:
        model = TemplateSettings
        fields = [
            'default_paper_size', 'default_font_size',
            'company_logo', 'company_name', 'company_address',
            'company_tax_id', 'company_phone', 'company_email',
            'company_website', 'footer_text',
        ]
        widgets = {
            'default_paper_size': forms.Select(attrs={
                'class': 'select',
            }),
            'default_font_size': forms.NumberInput(attrs={
                'class': 'input',
                'min': '8',
                'max': '24',
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Company name'),
            }),
            'company_address': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': '3',
                'placeholder': _('Company address'),
            }),
            'company_tax_id': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Tax ID / VAT number'),
            }),
            'company_phone': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Phone number'),
            }),
            'company_email': forms.EmailInput(attrs={
                'class': 'input',
                'placeholder': _('Email address'),
            }),
            'company_website': forms.URLInput(attrs={
                'class': 'input',
                'placeholder': _('https://example.com'),
            }),
            'footer_text': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': '3',
                'placeholder': _('Default footer text for all documents'),
            }),
        }
