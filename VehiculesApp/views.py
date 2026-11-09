from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import VehiculeForm
from .models import Vehicule


def liste_vehicules(request):
    vehicules = Vehicule.objects.select_related('entreprise').order_by('immatriculation')
    return render(request, 'vehicules/liste.html', {'vehicules': vehicules})


def detail_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule.objects.select_related('entreprise'), pk=pk)
    offres = (
        vehicule.offres
        .select_related('expedition', 'transporteur')
        .order_by('-date_proposition')
    )
    return render(request, 'vehicules/detail.html', {'vehicule': vehicule, 'offres': offres})


@require_POST
def supprimer_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    immatriculation = vehicule.immatriculation
    vehicule.delete()
    messages.success(request, f"Le véhicule {immatriculation} a été supprimé.")
    return redirect('vehicules:liste')


class VehiculeListView(ListView):
    model = Vehicule
    template_name = 'vehicules/liste.html'
    context_object_name = 'vehicules'

    def get_queryset(self):
        return Vehicule.objects.select_related('entreprise').order_by('immatriculation')


class VehiculeDetailView(DetailView):
    model = Vehicule
    template_name = 'vehicules/detail.html'
    context_object_name = 'vehicule'

    def get_queryset(self):
        return Vehicule.objects.select_related('entreprise')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offres'] = self.object.offres.select_related('expedition', 'transporteur').order_by('-date_proposition')
        return context


class VehiculeCreateView(CreateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'vehicules/form.html'
    success_url = reverse_lazy('vehicules:liste')

    def form_valid(self, form):
        messages.success(self.request, "Le véhicule a été ajouté.")
        return super().form_valid(form)


class VehiculeUpdateView(UpdateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'vehicules/form.html'
    success_url = reverse_lazy('vehicules:liste')

    def form_valid(self, form):
        messages.success(self.request, "Le véhicule a été modifié.")
        return super().form_valid(form)


class VehiculeDeleteView(DeleteView):
    model = Vehicule
    template_name = 'vehicules/confirm_delete.html'
    context_object_name = 'vehicule'
    success_url = reverse_lazy('vehicules:liste')

    def form_valid(self, form):
        messages.success(self.request, f"Le véhicule {self.object.immatriculation} a été supprimé.")
        return super().form_valid(form)
