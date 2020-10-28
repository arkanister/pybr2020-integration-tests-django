from django.apps import AppConfig
from django.utils.translation import ugettext_lazy


class NotesConfig(AppConfig):
    name = 'notes'
    verbose_name = ugettext_lazy('Notes')
