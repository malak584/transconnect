from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html

# Register your models here.
from OffresApp.models import Offre
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


class OffreInline(admin.StackedInline):
    model = Offre
    fk_name = 'expedition'
    extra = 0
    fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    readonly_fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


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
    date_hierarchy = 'date_souhaitee'
    list_per_page = 20
    inlines = [OffreInline]
    actions = ['cloturer_expeditions']

    @admin.action(description='Clôturer les expéditions sélectionnées')
    def cloturer_expeditions(self, request, queryset):
        total = queryset.count()
        a_cloturer = list(queryset.filter(statut='en cours'))
        cloturees = 0
        for exp in a_cloturer:
            exp.statut = 'livree'
            try:
                exp.full_clean()
                exp.save()
            except ValidationError as erreur:
                self.message_user(request, f"{exp.reference} : {' '.join(erreur.messages)}", level=messages.ERROR)
            else:
                cloturees += 1
        ignorees = total - len(a_cloturer)
        self.message_user(
            request,
            f"{cloturees} expédition(s) clôturée(s), {ignorees} ignorée(s) (statut différent de « en cours »).",
            level=messages.SUCCESS if cloturees else messages.WARNING,
        )

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
