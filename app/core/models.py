import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)

from django.contrib.auth import get_user_model

def user_image_file_path(instance, filename):
    """Generate file path for new user image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'user', filename)

def pest_image_file_path(instance, filename):
    """Generate file path for new pest image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'pest', filename)


class UserManager(models.Manager):
    def create_user(self, email, first_name, last_name, branch=None, password=None, **extra_fields):
        """Create and return a regular user with the provided details."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            branch=branch,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, first_name, last_name, branch=None, password=password, **extra_fields)

    def normalize_email(self, email):
        """Normalize the email address by lowercasing the domain part of it."""
        return email.lower()

    def get_by_natural_key(self, email):
        """Return the user with the given email."""
        return self.get(email=email)


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, null=True)
    branch = models.CharField(max_length=255, null=True)
    image = models.ImageField(null=True, upload_to=user_image_file_path)
    managers = models.ManyToManyField('self', symmetrical=False, related_name='managed_by', blank=True)
    is_technique = models.BooleanField(default=False)
    is_creator = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_short_name(self):
        return self.first_name
    
    def __str__(self):
        return self.email

    def assign_manager(self, manager):
        """Assign a manager to this user if the user is a creator."""
        if self.is_creator:
            self.managers.add(manager)
            self.save()
    
    @property
    def average_rating(self):
        if self.is_technique:
            return self.ratings_received.aggregate(models.Avg('rating'))['rating__avg']
        return None

    def create_manager(self, email, first_name, last_name, branch, password=None, **extra_fields):
        """Create a manager and assign them to the current user (owner)."""
        if self.is_creator:
            manager = User.objects.create_user(email, 
                                               first_name, 
                                               last_name, 
                                               branch, 
                                               password, 
                                               company=self.company, 
                                               **extra_fields)
            self.assign_manager(manager)
            return manager
        return None

class Rating(models.Model):
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings_received",
        limit_choices_to={'is_technique': True},
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings_given",
        limit_choices_to={'is_creator': True},
    )
    rating = models.PositiveSmallIntegerField()  # Calificación entre 1 y 5, por ejemplo
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating} for {self.technician.get_full_name()} by {self.creator.get_full_name()}"


class Register(models.Model):
    pest_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="registers")
    image = models.ImageField(null=True, upload_to=pest_image_file_path)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pest_name} ({self.owner.get_full_name()})"
    
class WorkRequest(models.Model):
    STATUS_CHOICES = [
        ('send', 'Send'),
        ('submitted', 'Submitted'),
        ('working', 'Working'),
    ]

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="sent_requests")
    technician = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request from {self.owner.get_full_name()} to {self.technician.get_full_name()} - Status: {self.status}"