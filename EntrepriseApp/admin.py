from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from VehiculesApp.models import Vehicule
from .models import Entreprise, Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informations TransConnect', {'fields': ('role', 'telephone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations TransConnect', {'fields': ('email', 'role', 'telephone')}),
    )
    list_display = ('username', 'user_id', 'role', 'first_name', 'last_name')
    list_filter = ('role', 'created_at')
    search_fields = ('username', 'user_id', 'role', 'first_name', 'last_name')
    list_editable = ('role', 'first_name', 'last_name')
    ordering = ('username',)
    date_hierarchy = 'created_at'
    list_per_page = 25


class VehiculeInline(admin.TabularInline):
    model = Vehicule
    extra = 0
    fields = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible')


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'gerant', 'created_at')
    list_display_links = ('matricule_fiscal',)
    list_filter = ('type_entreprise', 'created_at')
    search_fields = ('raison_sociale', 'matricule_fiscal', 'gerant__username')
    list_editable = ('raison_sociale',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('raison_sociale',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    inlines = [VehiculeInline]
    fieldsets = (
        ('Identité entreprise', {'fields': ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'adresse')}),
        ('Contact', {'fields': ('gerant',)}),
        ('Date système', {'fields': ('created_at', 'updated_at')}),
    )
