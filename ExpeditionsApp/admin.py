from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

# Register your models here.
from .models import Expedition


class EnRetard(admin.SimpleListFilter):
    title = 'Expéditions en retard'
    parameter_name = 'en_retard'

    def lookups(self, request, model_admin):
        return (
            ('oui', 'Oui'),
            ('non', 'Non'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'oui':
            return queryset.filter(date_souhaitee__lt=timezone.now().date(), statut__in=['publiee', 'en cours'])
        elif self.value() == 'non':
            return queryset.exclude(date_souhaitee__lt=timezone.now().date(), statut__in=['publiee', 'en cours'])
        return queryset


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrivee', 'date_souhaitee', 'poids_kg', 'statut_colore', 'statut', 'entreprise', 'created_at')
    list_filter = (EnRetard, 'statut', 'date_souhaitee', 'entreprise', 'created_at')
    list_editable = ('statut',)
    search_fields = ('reference', 'ville_depart', 'ville_arrivee', 'entreprise__raison_sociale')
    readonly_fields = ('reference', 'statut_colore', 'created_at', 'updated_at')
    fieldsets = (
        ('Trajet', {'fields': ('ville_depart', 'ville_arrivee', 'date_souhaitee')}),
        ('Marchandise', {'fields': ('reference', 'description', 'poids_kg')}),
        ('Gestion', {'fields': ('entreprise', 'statut')}),
        ('Suivi', {'fields': ('statut_colore', 'created_at', 'updated_at')}),
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    @admin.action(description='Marquer comme livrée')
    def make_it_livree(self, request, queryset):
        liste=queryset.filter(statut=['en cours'])
        for exp in liste:
            exp.statut='livree'
            try:
                exp.save()
            except validationError as error:
                errors.append(f"Erreur lors de la mise à jour de l'expédition {exp.reference}: {error}")
            

        actions = ["Marquer comme livrée"]

    @admin.display(description='Statut')
    def statut_colore(self, obj):
        couleurs = {
            'publiee': '#F0AD4E', 'en cours': '#5BC0DE', 'attribuee': '#337AB7',
            'livree': '#5CB85C', 'annulee': '#D9534F',
        }
        return format_html(
            '<span style="color:white;background:{};padding:3px 8px;border-radius:4px;">{}</span>',
            couleurs.get(obj.statut, '#999'), obj.get_statut_display(),
        )

