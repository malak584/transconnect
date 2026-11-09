from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from .models import Entreprise


def liste_entreprises(request):
    entreprises = (
        Entreprise.objects
        .select_related('gerant')
        .annotate(nb_vehicules=Count('vehicules', distinct=True), nb_expeditions=Count('expeditions', distinct=True))
        .order_by('raison_sociale')
    )
    return render(request, 'entreprises/liste.html', {'entreprises': entreprises})


def detail_entreprise(request, pk):
    entreprise = get_object_or_404(Entreprise.objects.select_related('gerant'), pk=pk)
    vehicules = entreprise.vehicules.order_by('immatriculation')
    expeditions = entreprise.expeditions.order_by('-created_at')
    offres = entreprise.offres.select_related('expedition', 'vehicule').order_by('-date_proposition')
    return render(request, 'entreprises/detail.html', {
        'entreprise': entreprise, 'vehicules': vehicules, 'expeditions': expeditions, 'offres': offres,
    })


class EntrepriseListView(ListView):
    model = Entreprise
    template_name = 'entreprises/liste.html'
    context_object_name = 'entreprises'

    def get_queryset(self):
        return (
            Entreprise.objects
            .select_related('gerant')
            .annotate(nb_vehicules=Count('vehicules', distinct=True), nb_expeditions=Count('expeditions', distinct=True))
            .order_by('raison_sociale')
        )


class EntrepriseDetailView(DetailView):
    model = Entreprise
    template_name = 'entreprises/detail.html'
    context_object_name = 'entreprise'

    def get_queryset(self):
        return Entreprise.objects.select_related('gerant')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicules'] = self.object.vehicules.order_by('immatriculation')
        context['expeditions'] = self.object.expeditions.order_by('-created_at')
        context['offres'] = self.object.offres.select_related('expedition', 'vehicule').order_by('-date_proposition')
        return context
