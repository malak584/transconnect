from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

# Create your models here.
class Expedition(models.Model):
    reference=models.CharField(max_length=12,unique=True,editable=False,validators=[RegexValidator(r'^EXP-\d{2}-\d{5}$',"La référence doit suivre le format EXP-AA-NNNNN.")])
    ville_depart=models.CharField(max_length=100)
    ville_arrivee=models.CharField(max_length=100)
    date_souhaitee=models.DateField()
    description=models.TextField()
    poids_kg=models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), "Le poids doit être supérieur à 0")])
    statut=models.CharField(max_length=20,choices=[('publiee','publiee'),('en cours','en cours'),('attribuee','attribuee'),('livree','livree'),('annulee','annulee')],default='publiee')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    entreprise=models.ForeignKey('EntrepriseApp.Entreprise',related_name='expeditions',on_delete=models.CASCADE)

    def __str__(self):
        return self.reference

    def _generate_reference(self):
        # format EXP-AA-NNNNN : AA = année de création, NNNNN = compteur 00001-99999 remis à zéro chaque année
        prefix = f"EXP-{timezone.now().year % 100:02d}-"
        derniere = type(self).objects.filter(reference__startswith=prefix).order_by('-reference').values_list('reference', flat=True).first()
        numero = int(derniere[-5:]) + 1 if derniere else 1
        if numero > 99999:
            raise ValidationError("Le nombre maximum d'expéditions (99999) est atteint pour cette année.")
        return f"{prefix}{numero:05d}"

    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError({'entreprise': "L'expédition doit être publiée par une entreprise de type chargeur."})

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        self.full_clean()
        super().save(*args, **kwargs)
