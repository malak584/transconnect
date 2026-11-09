from django import forms

from .models import Expedition


class ExpeditionForm(forms.ModelForm):
    class Meta:
        model = Expedition
        fields = ['ville_depart', 'ville_arrivee', 'date_souhaitee', 'description', 'poids_kg']
        widgets = {
            'date_souhaitee': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
