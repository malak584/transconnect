from django.contrib import admin

# Register your models here.
from .models import Vehicule


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible', 'entreprise', 'created_at')
    list_filter = ('type_vehicule', 'disponible', 'entreprise', 'created_at')
    search_fields = ('immatriculation', 'entreprise__raison_sociale')
    list_editable = ('disponible',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Véhicule', {'fields': ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible')}),
        ('Propriétaire', {'fields': ('entreprise',)}),
        ('Date système', {'fields': ('created_at', 'updated_at')}),
    )
    ordering = ('immatriculation',)
    date_hierarchy = 'created_at'
    list_per_page = 20

