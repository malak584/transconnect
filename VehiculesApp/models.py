from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.
# charge maximale indicative (en kg) par type de véhicule
CHARGE_MAX_KG = {
    'camionnette': 1500,
    'fourgon': 3500,
    'camion_porteur': 19000,
    'semi_remorque': 26000,
}

class Vehicule(models.Model):
    immatriculation=models.CharField(max_length=10,unique=True)
    type_vehicule=models.CharField(max_length=20,choices=[('camionnette','Camionnette / utilitaire léger'),('camion_porteur','Camion porteur'),('semi_remorque','Semi-remorque'),('fourgon','Fourgon')])
    capacite_kg=models.PositiveIntegerField(validators=[MinValueValidator(1, "La capacité doit être supérieure à 0")])
    disponible=models.BooleanField(default=True)
    entreprise=models.ForeignKey('EntrepriseApp.Entreprise',related_name='vehicules',on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.immatriculation

    def peut_transporter(self, poids_kg):
        return poids_kg <= CHARGE_MAX_KG[self.type_vehicule]

    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != 'transporteur':
            raise ValidationError({'entreprise': "Le véhicule doit appartenir à une entreprise de type transporteur."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
