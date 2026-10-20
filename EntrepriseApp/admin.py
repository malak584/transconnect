from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import Entreprise, Utilisateur

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
    list_per_page = 1


class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'gerant', 'created_at')
    list_filter = ('type_entreprise', 'created_at')
    search_fields = ('raison_sociale', 'matricule_fiscal', 'gerant__username')
    ordering = ('raison_sociale',)
    date_hierarchy = 'created_at'
    list_per_page = 20


admin.site.register(Entreprise, EntrepriseAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)
