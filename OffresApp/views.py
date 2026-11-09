from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from EntrepriseApp.models import Entreprise
from .forms import OffreForm, OffreModifForm
from .models import Offre


def liste_offres(request):
    offres = (
        Offre.objects
        .select_related('expedition', 'transporteur', 'vehicule')
        .order_by('-date_proposition', '-id')
    )
    return render(request, 'offres/liste.html', {'offres': offres})


def detail_offre(request, pk):
    offre = get_object_or_404(Offre.objects.select_related('expedition', 'transporteur', 'vehicule'), pk=pk)
    return render(request, 'offres/detail.html', {'offre': offre})


@require_POST
def supprimer_offre(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    offre.delete()
    messages.success(request, f"L'offre n°{pk} a été supprimée.")
    return redirect('offres:liste')


class OffreListView(ListView):
    model = Offre
    template_name = 'offres/liste.html'
    context_object_name = 'offres'

    def get_queryset(self):
        return Offre.objects.select_related('expedition', 'transporteur', 'vehicule').order_by('-date_proposition', '-id')


class OffreDetailView(DetailView):
    model = Offre
    template_name = 'offres/detail.html'
    context_object_name = 'offre'

    def get_queryset(self):
        return Offre.objects.select_related('expedition', 'transporteur', 'vehicule')


class OffreCreateView(CreateView):
    model = Offre
    form_class = OffreForm
    template_name = 'offres/form.html'

    def get_entreprise_courante(self):
        return get_object_or_404(Entreprise, pk=self.kwargs['entreprise_id'], type_entreprise='transporteur')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['transporteur'] = self.get_entreprise_courante()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entreprise'] = self.get_entreprise_courante()
        return context

    def form_valid(self, form):
        form.instance.transporteur = self.get_entreprise_courante()
        try:
            response = super().form_valid(form)
        except ValidationError as erreur:
            form.add_error(None, erreur.messages)
            return self.form_invalid(form)
        messages.success(self.request, "Votre offre a été envoyée.")
        return response

    def get_success_url(self):
        return reverse('expeditions:detail', kwargs={'reference': self.object.expedition.reference})


class OffreUpdateView(UpdateView):
    model = Offre
    form_class = OffreModifForm
    template_name = 'offres/form.html'

    def get_queryset(self):
        return Offre.objects.filter(statut='proposee').select_related('expedition', 'transporteur')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ValidationError as erreur:
            form.add_error(None, erreur.messages)
            return self.form_invalid(form)
        messages.success(self.request, "L'offre a été modifiée.")
        return response

    def get_success_url(self):
        return reverse('offres:detail', kwargs={'pk': self.object.pk})


class OffreDeleteView(DeleteView):
    model = Offre
    template_name = 'offres/confirm_delete.html'
    context_object_name = 'offre'
    success_url = reverse_lazy('offres:liste')

    def get_queryset(self):
        return Offre.objects.select_related('expedition', 'transporteur')

    def form_valid(self, form):
        messages.success(self.request, f"L'offre n°{self.object.pk} a été supprimée.")
        return super().form_valid(form)
