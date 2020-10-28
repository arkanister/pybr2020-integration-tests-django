from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Note(models.Model):
    title = models.CharField(
        _('Title'), max_length=100)

    content = models.TextField(
        _('Content'), null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name=_('notes'),
        verbose_name=_('User'),
        on_delete=models.CASCADE)

    category = models.ForeignKey(
        'notes.Category',
        related_name=_('notes'),
        verbose_name=_('Category'),
        on_delete=models.CASCADE,
        null=True, blank=True)

    archived = models.BooleanField(
        _('Archived'), default=False)

    created_at = models.DateTimeField(
        _('Created At'), auto_now_add=True)

    last_update = models.DateTimeField(
        _('Last Update'), auto_now=True)

    class Meta:
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')
        ordering = ('category', '-created_at')

    def __str__(self):
        return self.title
