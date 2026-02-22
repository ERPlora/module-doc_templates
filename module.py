from django.utils.translation import gettext_lazy as _

MODULE_ID = 'doc_templates'
MODULE_NAME = _('Document Templates')
MODULE_VERSION = '1.0.0'
MODULE_ICON = 'document-text-outline'
MODULE_DESCRIPTION = _('Customizable document templates for receipts, invoices, and reports')
MODULE_AUTHOR = 'ERPlora'
MODULE_CATEGORY = 'documents'

MENU = {
    'label': _('Templates'),
    'icon': 'document-text-outline',
    'order': 75,
}

NAVIGATION = [
    {'label': _('Templates'), 'icon': 'document-text-outline', 'id': 'dashboard'},
    {'label': _('Variables'), 'icon': 'code-outline', 'id': 'variables'},
    {'label': _('Settings'), 'icon': 'settings-outline', 'id': 'settings'},
]

DEPENDENCIES = []

PERMISSIONS = [
    'doc_templates.view_template',
    'doc_templates.add_template',
    'doc_templates.change_template',
    'doc_templates.delete_template',
    'doc_templates.manage_settings',
]
