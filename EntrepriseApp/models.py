import re

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone

# Create your models here.
class UtilisateurManager(UserManager):
    def _generate_user_id(self):
        # format AAuserNN : AA = année d'inscription, NN = compteur 00-99 remis à zéro chaque année
        prefix = f"{timezone.now().year % 100:02d}user"
        dernier = self.filter(user_id__startswith=prefix).order_by('-user_id').values_list('user_id', flat=True).first()
        numero = int(dernier[-2:]) + 1 if dernier else 0
        if numero > 99:
            raise ValidationError("Le nombre maximum d'utilisateurs (100) est atteint pour cette année.")
        return f"{prefix}{numero:02d}"

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('user_id', self._generate_user_id())
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('user_id', self._generate_user_id())
        return super().create_superuser(username, email, password, **extra_fields)
def EmailValidate(value):
    if value.rsplit('@', 1)[-1].lower() != 'gmail.com':
        raise ValidationError("L'adresse e-mail doit appartenir au domaine gmail.com.")

class Utilisateur(AbstractUser):
    user_id=models.CharField(max_length=8,editable=False,primary_key=True,validators=[RegexValidator(r'^\d{2}user\d{2}$',"Le user_id doit suivre le format AAuserNN.")])
    email=models.EmailField(unique=True,validators=[EmailValidate])
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
    matricule_fiscal=models.CharField(max_length=17,unique=True,validators=[RegexValidator(r'^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$',"Matricule fiscal invalide (ex. 1234567AAM000 ou 1234567/A/A/M/000).")])
    type_entreprise=models.CharField(max_length=20,choices=[('chargeur','chargeur'),('transporteur','transporteur')],default='chargeur')
    adresse=models.TextField(validators=[MinLengthValidator(20,"L'adresse doit contenir au moins 20 caractères.")])
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    gerant=models.OneToOneField(Utilisateur,related_name='entreprise',on_delete=models.CASCADE)

    def __str__(self):
        return self.raison_sociale

    def clean(self):
        super().clean()
        # on stocke le matricule sans séparateurs, sinon "1234567/A/A/M/000" et "1234567AAM000" passeraient comme deux valeurs uniques
        if self.matricule_fiscal:
            self.matricule_fiscal = re.sub(r'[/ -]', '', self.matricule_fiscal).upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
