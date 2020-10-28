from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def create(self, name, email, password=None, **kwargs):
        """
        Creates a valid user based on name, email and password.
        """
        instance = self.model(name=name, email=email, **kwargs)
        instance.set_password(password)
        instance.save()

        return instance
