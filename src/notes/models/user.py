from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from notes.managers.user import UserManager


class User(AbstractBaseUser):

    name = models.CharField(
        _('Name'), max_length=60)

    email = models.EmailField(
        _('Email'), unique=True)

    date_joined = models.DateTimeField(
        _('Joined Date'), default=timezone.now)

    is_active = models.BooleanField(
        _('Active'), default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_superuser(self):
        """ Disable superusers roles. """
        return False

    @property
    def is_staff(self):
        """
        It's no longer necessary to keep staff users since
        the administration is not enabled.
        """
        return False
