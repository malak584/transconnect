from django.db import models

# Create your models here.
class Offre(models.Model):
    prix=models.DecimalField(max_digits=10, decimal_places=2)
    delai_jours=models.PositiveIntegerField()
    statut=models.CharField(max_length=20,choices=[('proposee','proposee'),('acceptee','acceptee'),('refusee','refusee'),('retiree','retiree')],default='proposee')
    date_proposition=models.DateField(auto_now_add=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    expedition=models.ForeignKey('ExpeditionsApp.Expedition',related_name='offres',on_delete=models.CASCADE)
    transporteur=models.ForeignKey('EntrepriseApp.Entreprise',related_name='offres',on_delete=models.CASCADE)
    vehicule=models.ForeignKey('VehiculesApp.Vehicule',related_name='offres',on_delete=models.CASCADE)

    def __str__(self):
        return f"Offre {self.id} - Expedition {self.expedition.reference} - Transporteur {self.transporteur.raison_sociale}"
