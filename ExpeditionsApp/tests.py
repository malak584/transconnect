import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from EntrepriseApp.models import Entreprise, Utilisateur
from .models import Expedition

# Create your tests here.
def creer_entreprise(type_entreprise, n):
    gerant = Utilisateur.objects.create_user(f"g{n}", f"g{n}@gmail.com", 'motdepasse', telephone='12345678')
    return Entreprise.objects.create(raison_sociale=f"Ste {n}", matricule_fiscal=f"123456{n}AAM000", type_entreprise=type_entreprise,
                                     adresse='12 rue de la Liberté, Tunis', gerant=gerant)


class ExpeditionTest(TestCase):
    def setUp(self):
        self.chargeur = creer_entreprise('chargeur', 1)
        self.transporteur = creer_entreprise('transporteur', 2)

    def expedition(self, **kwargs):
        valeurs = dict(ville_depart='Tunis', ville_arrivee='Sfax', date_souhaitee=datetime.date(2026, 12, 1),
                       description='Palettes', poids_kg=500, entreprise=self.chargeur)
        valeurs.update(kwargs)
        return Expedition(**valeurs)

    def test_reference_suit_le_format_EXP_AA_NNNNN(self):
        aa = f"{timezone.now().year % 100:02d}"
        e1, e2 = self.expedition(), self.expedition()
        e1.save()
        e2.save()
        self.assertEqual(e1.reference, f"EXP-{aa}-00001")
        self.assertEqual(e2.reference, f"EXP-{aa}-00002")

    def test_compteur_limite_a_99999_par_annee(self):
        aa = f"{timezone.now().year % 100:02d}"
        e = self.expedition()
        e.save()
        Expedition.objects.filter(pk=e.pk).update(reference=f"EXP-{aa}-99999")
        with self.assertRaises(ValidationError):
            self.expedition().save()

    def test_poids_nul_refuse(self):
        with self.assertRaises(ValidationError) as ctx:
            self.expedition(poids_kg=0).save()
        self.assertIn('poids_kg', ctx.exception.message_dict)

    def test_entreprise_doit_etre_chargeur(self):
        with self.assertRaises(ValidationError) as ctx:
            self.expedition(entreprise=self.transporteur).save()
        self.assertIn('entreprise', ctx.exception.message_dict)
