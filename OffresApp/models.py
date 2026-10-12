from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

# Create your models here.
class Offre(models.Model):
    prix=models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), "Le prix doit être supérieur à 0")])
    delai_jours=models.PositiveIntegerField(validators=[MinValueValidator(1, "Le délai doit être d'au moins 1 jour")])
    statut=models.CharField(max_length=20,choices=[('proposee','proposee'),('acceptee','acceptee'),('refusee','refusee'),('retiree','retiree')],default='proposee')
    date_proposition=models.DateField(auto_now_add=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    expedition=models.ForeignKey('ExpeditionsApp.Expedition',related_name='offres',on_delete=models.CASCADE)
    transporteur=models.ForeignKey('EntrepriseApp.Entreprise',related_name='offres',on_delete=models.CASCADE)
    vehicule=models.ForeignKey('VehiculesApp.Vehicule',related_name='offres',on_delete=models.CASCADE)

    def __str__(self):
        return f"Offre {self.id} - Expedition {self.expedition.reference} - Transporteur {self.transporteur.raison_sociale}"

    def clean(self):
        super().clean()
        erreurs = {}

        def erreur(champ, message):
            erreurs.setdefault(champ, []).append(message)

        # 1. seul un transporteur peut faire une offre
        if self.transporteur_id and self.transporteur.type_entreprise != 'transporteur':
            erreur('transporteur', "Une offre ne peut être créée que par une entreprise de type transporteur.")
        # 2. le véhicule doit appartenir au transporteur de l'offre
        if self.vehicule_id and self.transporteur_id and self.vehicule.entreprise_id != self.transporteur_id:
            erreur('vehicule', "Le véhicule doit appartenir à l'entreprise qui fait l'offre.")
        # 3. et 6. ne concernent que les nouvelles offres
        if self._state.adding:
            if self.expedition_id and self.expedition.statut != 'publiee':
                erreur('expedition', "Cette expédition ne reçoit plus d'offres (statut différent de publiee).")
            if self.vehicule_id and not self.vehicule.disponible:
                erreur('vehicule', "Ce véhicule n'est pas disponible.")
        # 4. une seule offre proposee par transporteur et par expédition
        if self.statut == 'proposee' and self.expedition_id and self.transporteur_id:
            doublon = type(self).objects.filter(expedition_id=self.expedition_id, transporteur_id=self.transporteur_id, statut='proposee').exclude(pk=self.pk)
            if doublon.exists():
                erreur('statut', "Ce transporteur a déjà une offre proposee sur cette expédition.")
        # 7. compatibilité type de véhicule / poids de l'expédition
        if self.vehicule_id and self.expedition_id and not self.vehicule.peut_transporter(self.expedition.poids_kg):
            erreur('vehicule', "Le type de véhicule ne permet pas de transporter le poids de cette expédition.")

        if erreurs:
            raise ValidationError(erreurs)

    def save(self, *args, **kwargs):
        ancien_statut = type(self).objects.filter(pk=self.pk).values_list('statut', flat=True).first() if self.pk else None
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            # 5. cascade à l'acceptation (uniquement au passage à acceptee)
            if self.statut == 'acceptee' and ancien_statut != 'acceptee':
                self.expedition.statut = 'attribuee'
                self.expedition.save()
                type(self).objects.filter(expedition=self.expedition, statut='proposee').exclude(pk=self.pk).update(statut='refusee', updated_at=timezone.now())
