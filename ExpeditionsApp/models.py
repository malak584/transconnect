from django.db import models

# Create your models here.
class Expedition(models.Model):
    reference=models.CharField(max_length=10,unique=True)
    ville_depart=models.CharField(max_length=100)
    ville_arrivee=models.CharField(max_length=100)
    date_souhaitee=models.DateField()
    description=models.TextField()
    poids_kg=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    statut=models.CharField(max_length=20,choices=[('publiee','publiee'),('en cours','en cours'),('attribuee','attribuee'),('livree','livree'),('annulee','annulee')],default='publiee')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    entreprise=models.ForeignKey('EntrepriseApp.Entreprise',related_name='expeditions',on_delete=models.CASCADE)

    def __str__(self):
        return self.reference
