from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

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
