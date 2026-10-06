from django.db import models

# Create your models here.
class Vehicule(models.Model):
    immatriculation=models.CharField(max_length=10,unique=True)
    capacite_kg=models.PositiveIntegerField()
    disponibilite=models.BooleanField(default=True)
    entreprise=models.ForeignKey('EntrepriseApp.Entreprise',related_name='vehicules',on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.immatriculation
