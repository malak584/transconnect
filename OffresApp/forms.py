from django import forms

from ExpeditionsApp.models import Expedition
from VehiculesApp.models import Vehicule
from .models import Offre


class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ['expedition', 'vehicule', 'prix', 'delai_jours']

    def __init__(self, *args, transporteur=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expedition'].queryset = Expedition.objects.filter(statut='publiee')
        self.fields['vehicule'].queryset = Vehicule.objects.filter(entreprise=transporteur, disponible=True)


class OffreModifForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ['prix', 'delai_jours']
