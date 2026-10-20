from django.contrib import admin

# Register your models here.
from .models import Offre


class OffreAdmin(admin.ModelAdmin):
    list_display = ('id', 'expedition', 'transporteur', 'vehicule', 'prix', 'delai_jours', 'statut', 'date_proposition')
    list_filter = ('statut', 'date_proposition', 'transporteur')
    search_fields = ('expedition__reference', 'transporteur__raison_sociale', 'vehicule__immatriculation')
    ordering = ('-created_at',)
    date_hierarchy = 'date_proposition'
    list_per_page = 20


admin.site.register(Offre, OffreAdmin)
