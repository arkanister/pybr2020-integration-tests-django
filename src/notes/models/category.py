from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    name = models.CharField(
        _('Name'), max_length=40)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='categories',
        verbose_name=_('User'),
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def __str__(self):
        return self.name
