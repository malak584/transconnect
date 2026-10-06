import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

# Create your models here.
class UtilisateurManager(UserManager):
    def _generate_user_id(self):
        while True:
            user_id = uuid.uuid4().hex[:8].upper()
            if not self.filter(pk=user_id).exists():
                return user_id

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('user_id', self._generate_user_id())
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('user_id', self._generate_user_id())
        return super().create_superuser(username, email, password, **extra_fields)


class utilisateur(AbstractUser):
    user_id=models.CharField(max_length=8,editable=False,primary_key=True)
    email=models.EmailField(unique=True)
    role=models.CharField(max_length=20,choices=[('administrateur','administrateur'),('chargeur','chargeur'),('transporteur','transporteur')],default='chargeur')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    telephone=models.CharField(max_length=8)

    objects = UtilisateurManager()

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = type(self).objects._generate_user_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class Entreprise(models.Model):
    raison_sociale=models.CharField(max_length=100)
    matricule_fiscale=models.CharField(max_length=17,unique=True)
    type_entreprise=models.CharField(max_length=20,choices=[('chargeur','chargeur'),('transporteur','transporteur')],default='chargeur')
    adresse=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    gerant=models.OneToOneField(utilisateur,related_name='entreprise',on_delete=models.CASCADE)

    def __str__(self):
        return self.raison_sociale
