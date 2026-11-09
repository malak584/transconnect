import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from EntrepriseApp.models import Entreprise, Utilisateur
from ExpeditionsApp.models import Expedition
from VehiculesApp.models import Vehicule
from .models import Offre

# Create your tests here.
def creer_entreprise(type_entreprise, n):
    gerant = Utilisateur.objects.create_user(f"g{n}", f"g{n}@gmail.com", 'motdepasse', telephone='12345678')
    return Entreprise.objects.create(raison_sociale=f"Ste {n}", matricule_fiscal=f"123456{n}AAM000", type_entreprise=type_entreprise,
                                     adresse='12 rue de la Liberté, Tunis', gerant=gerant)


class OffreTest(TestCase):
    def setUp(self):
        self.chargeur = creer_entreprise('chargeur', 1)
        self.transporteur = creer_entreprise('transporteur', 2)
        self.autre_transporteur = creer_entreprise('transporteur', 3)
        self.vehicule = Vehicule.objects.create(immatriculation='111TUN1', type_vehicule='camion_porteur', capacite_kg=10000, entreprise=self.transporteur)
        self.autre_vehicule = Vehicule.objects.create(immatriculation='222TUN2', type_vehicule='camion_porteur', capacite_kg=10000, entreprise=self.autre_transporteur)
        self.expedition = Expedition.objects.create(ville_depart='Tunis', ville_arrivee='Sfax', date_souhaitee=datetime.date(2026, 12, 1),
                                                    description='Palettes', poids_kg=5000, entreprise=self.chargeur)

    def offre(self, **kwargs):
        valeurs = dict(prix=800, delai_jours=2, expedition=self.expedition, transporteur=self.transporteur, vehicule=self.vehicule)
        valeurs.update(kwargs)
        return Offre(**valeurs)

    def assertRefusee(self, offre, champ):
        with self.assertRaises(ValidationError) as ctx:
            offre.save()
        self.assertIn(champ, ctx.exception.message_dict)

    def test_offre_valide(self):
        o = self.offre()
        o.save()
        self.assertEqual(o.statut, 'proposee')

    def test_prix_et_delai_positifs(self):
        self.assertRefusee(self.offre(prix=0), 'prix')
        self.assertRefusee(self.offre(delai_jours=0), 'delai_jours')

    def test_regle1_transporteur_uniquement(self):
        self.assertRefusee(self.offre(transporteur=self.chargeur), 'transporteur')

    def test_regle2_vehicule_du_meme_transporteur(self):
        self.assertRefusee(self.offre(vehicule=self.autre_vehicule), 'vehicule')

    def test_regle3_expedition_publiee_uniquement(self):
        self.expedition.statut = 'annulee'
        self.expedition.save()
        self.assertRefusee(self.offre(), 'expedition')

    def test_regle4_une_seule_offre_proposee_par_transporteur(self):
        self.offre().save()
        self.assertRefusee(self.offre(prix=700), 'statut')
        self.offre(transporteur=self.autre_transporteur, vehicule=self.autre_vehicule).save()

    def test_regle4_nouvelle_offre_possible_apres_retrait(self):
        o = self.offre()
        o.save()
        o.statut = 'retiree'
        o.save()
        self.offre(prix=700).save()

    def test_regle5_cascade_a_l_acceptation(self):
        o1 = self.offre()
        o1.save()
        o2 = self.offre(transporteur=self.autre_transporteur, vehicule=self.autre_vehicule)
        o2.save()
        o1.statut = 'acceptee'
        o1.save()
        o2.refresh_from_db()
        self.expedition.refresh_from_db()
        self.assertEqual(o1.statut, 'acceptee')
        self.assertEqual(o2.statut, 'refusee')
        self.assertEqual(self.expedition.statut, 'attribuee')

    def test_regle5_pas_de_cascade_sur_une_offre_deja_acceptee(self):
        o = self.offre()
        o.save()
        o.statut = 'acceptee'
        o.save()
        self.expedition.refresh_from_db()
        self.expedition.statut = 'livree'
        self.expedition.save()
        o.prix = 900
        o.save()
        self.expedition.refresh_from_db()
        self.assertEqual(self.expedition.statut, 'livree')

    def test_regle6_vehicule_indisponible(self):
        self.vehicule.disponible = False
        self.vehicule.save()
        self.assertRefusee(self.offre(), 'vehicule')

    def test_regle7_type_vehicule_et_poids(self):
        petit = Vehicule.objects.create(immatriculation='333TUN3', type_vehicule='camionnette', capacite_kg=1500, entreprise=self.transporteur)
        self.assertRefusee(self.offre(vehicule=petit), 'vehicule')
        self.expedition.poids_kg = 1000
        self.expedition.save()
        self.offre(vehicule=petit).save()


class OffreAdminExportTest(TestCase):
    def test_export_csv_declare_sur_offreadmin(self):
        from django.contrib import admin
        from .admin import exporter_offres_csv
        self.assertIn(exporter_offres_csv, admin.site._registry[Offre].actions)
