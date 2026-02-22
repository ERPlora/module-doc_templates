from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DocTemplatesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'doc_templates'
    label = 'doc_templates'
    verbose_name = _('Document Templates')

    def ready(self):
        pass
