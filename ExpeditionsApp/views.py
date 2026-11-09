from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from EntrepriseApp.models import Entreprise
from .forms import ExpeditionForm
from .models import Expedition


def liste_expeditions(request):
    expeditions = (
        Expedition.objects
        .filter(statut='publiee')
        .select_related('entreprise')
        .order_by('-created_at')
    )
    return render(request, 'expeditions/liste.html', {'expeditions': expeditions})


def detail_expedition(request, reference):
    expedition = get_object_or_404(Expedition.objects.select_related('entreprise'), reference=reference)
    offres = (
        expedition.offres
        .select_related('transporteur', 'vehicule')
        .order_by('-date_proposition')
    )
    return render(request, 'expeditions/detail.html', {'expedition': expedition, 'offres': offres})


@require_POST
def supprimer_expedition(request, reference):
    expedition = get_object_or_404(Expedition, reference=reference)
    expedition.delete()
    messages.success(request, f"L'expédition {reference} a été supprimée.")
    return redirect('expeditions:liste')


class ExpeditionListView(ListView):
    model = Expedition
    template_name = 'expeditions/liste.html'
    context_object_name = 'expeditions'

    def get_queryset(self):
        return (
            Expedition.objects
            .filter(statut='publiee')
            .select_related('entreprise')
            .order_by('-created_at')
        )


class ExpeditionDetailView(DetailView):
    model = Expedition
    template_name = 'expeditions/detail.html'
    context_object_name = 'expedition'
    slug_field = 'reference'
    slug_url_kwarg = 'reference'

    def get_queryset(self):
        return Expedition.objects.select_related('entreprise')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offres'] = self.object.offres.select_related('transporteur', 'vehicule').order_by('-date_proposition')
        return context


class ExpeditionCreateView(CreateView):
    model = Expedition
    form_class = ExpeditionForm
    template_name = 'expeditions/form.html'

    def get_entreprise_courante(self):
        return get_object_or_404(Entreprise, pk=self.kwargs['entreprise_id'], type_entreprise='chargeur')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entreprise'] = self.get_entreprise_courante()
        return context

    def form_valid(self, form):
        form.instance.entreprise = self.get_entreprise_courante()
        messages.success(self.request, "L'expédition a été publiée.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('expeditions:detail', kwargs={'reference': self.object.reference})


class ExpeditionUpdateView(UpdateView):
    model = Expedition
    form_class = ExpeditionForm
    template_name = 'expeditions/form.html'
    slug_field = 'reference'
    slug_url_kwarg = 'reference'

    def form_valid(self, form):
        messages.success(self.request, "L'expédition a été modifiée.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('expeditions:detail', kwargs={'reference': self.object.reference})


class ExpeditionDeleteView(DeleteView):
    model = Expedition
    template_name = 'expeditions/confirm_delete.html'
    context_object_name = 'expedition'
    slug_field = 'reference'
    slug_url_kwarg = 'reference'
    success_url = reverse_lazy('expeditions:liste')

    def form_valid(self, form):
        messages.success(self.request, f"L'expédition {self.object.reference} a été supprimée.")
        return super().form_valid(form)
