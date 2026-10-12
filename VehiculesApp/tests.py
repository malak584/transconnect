from django.core.exceptions import ValidationError
from django.test import TestCase

from EntrepriseApp.models import Entreprise, Utilisateur
from .models import Vehicule

# Create your tests here.
def creer_entreprise(type_entreprise, n):
    gerant = Utilisateur.objects.create_user(f"g{n}", f"g{n}@gmail.com", 'motdepasse', telephone='12345678')
    return Entreprise.objects.create(raison_sociale=f"Ste {n}", matricule_fiscal=f"123456{n}AAM000", type_entreprise=type_entreprise,
                                     adresse='12 rue de la Liberté, Tunis', gerant=gerant)


class VehiculeTest(TestCase):
    def setUp(self):
        self.transporteur = creer_entreprise('transporteur', 1)
        self.chargeur = creer_entreprise('chargeur', 2)

    def test_capacite_nulle_refusee(self):
        v = Vehicule(immatriculation='111TUN1', type_vehicule='fourgon', capacite_kg=0, entreprise=self.transporteur)
        with self.assertRaises(ValidationError) as ctx:
            v.save()
        self.assertIn('capacite_kg', ctx.exception.message_dict)

    def test_entreprise_doit_etre_transporteur(self):
        v = Vehicule(immatriculation='111TUN1', type_vehicule='fourgon', capacite_kg=3000, entreprise=self.chargeur)
        with self.assertRaises(ValidationError) as ctx:
            v.save()
        self.assertIn('entreprise', ctx.exception.message_dict)
        v.entreprise = self.transporteur
        v.save()

    def test_compatibilite_type_et_poids(self):
        v = Vehicule(type_vehicule='camionnette')
        self.assertTrue(v.peut_transporter(1500))
        self.assertFalse(v.peut_transporter(1500.01))
        self.assertTrue(Vehicule(type_vehicule='semi_remorque').peut_transporter(26000))
        self.assertFalse(Vehicule(type_vehicule='fourgon').peut_transporter(4000))
