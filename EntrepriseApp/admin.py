from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from VehiculesApp.models import Vehicule
from .models import Entreprise, Utilisateur
@admin.site_header = "TransConnect Administration"
@admin.site_title = "TransConnect Admin Portal"
@admin.site_index_title = "Welcome to TransConnect Admin Portal"


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


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'gerant', 'created_at')
    list_filter = ('type_entreprise', 'created_at')
    search_fields = ('raison_sociale', 'matricule_fiscal', 'gerant__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Identité entreprise', {'fields': ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'adresse')}),
        ('Contact', {'fields': ('gerant',)}),
        ('Date système', {'fields': ('created_at', 'updated_at')}),
    )

class vehiculeInline(admin.StackedInline):
    model = Vehicule
    field="immatriculation"
    extra = 1
    
    readonly_fields = ('created_at', 'updated_at')
    can_delete = False
