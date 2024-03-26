from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password


class User(AbstractUser):
    image = models.ImageField(upload_to='users_images', blank=True, null=True, verbose_name='Аватар')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    two_step_auth = models.BooleanField(default=False)

    class Meta:
        db_table = 'user'
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

class TemporaryUser(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=150)
    unique_code = models.CharField(max_length=6)

    class Meta:
        db_table = "TemporaryUser"
        verbose_name = "Временный пользователь"

    def convert_to_user(self):
        user = User(username=self.username, email=self.email)
        user.password = make_password(self.password)
        user.save()
        return user