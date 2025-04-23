from django.contrib.auth.models import AbstractBaseUser , BaseUserManager
from django.db import models
from django.contrib.auth.hashers import make_password

class AccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # Use set_password to hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superadmin', True)

        return self.create_user(email, username, password, **extra_fields)

class Account(AbstractBaseUser ):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'  # Use email as the unique identifier
    REQUIRED_FIELDS = ['username']  # Fields required when creating a user

    objects = AccountManager()

    def __str__(self):
        return self.email