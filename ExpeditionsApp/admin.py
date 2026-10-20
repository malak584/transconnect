from django.contrib import admin

# Register your models here.
from .models import Expedition


class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrivee', 'date_souhaitee', 'poids_kg', 'statut', 'entreprise', 'created_at')
    list_filter = ('statut', 'date_souhaitee', 'entreprise', 'created_at')
    search_fields = ('reference', 'ville_depart', 'ville_arrivee', 'entreprise__raison_sociale')
    readonly_fields = ('reference',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20


admin.site.register(Expedition, ExpeditionAdmin)
