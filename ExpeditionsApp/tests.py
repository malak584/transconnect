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


class ExpeditionAdminActionTest(TestCase):
    def setUp(self):
        chargeur = creer_entreprise('chargeur', 1)
        self.admin_user = Utilisateur.objects.create_superuser('boss', 'boss@gmail.com', 'motdepasse', telephone='12345678')
        self.client.force_login(self.admin_user)
        self.exps = {}
        for statut in ('publiee', 'en cours', 'attribuee', 'livree', 'annulee'):
            e = Expedition(ville_depart='Tunis', ville_arrivee='Sfax', date_souhaitee=datetime.date(2026, 12, 1),
                           description='Palettes', poids_kg=500, entreprise=chargeur, statut=statut)
            e.save()
            self.exps[statut] = e

    def lancer_action(self, ids):
        return self.client.post('/admin/ExpeditionsApp/expedition/', {
            'action': 'cloturer_expeditions', '_selected_action': ids, 'index': 0,
        }, follow=True)

    def test_seules_les_expeditions_en_cours_sont_cloturees(self):
        self.lancer_action([e.pk for e in self.exps.values()])
        for statut, e in self.exps.items():
            e.refresh_from_db()
            attendu = 'livree' if statut == 'en cours' else statut
            self.assertEqual(e.statut, attendu, statut)

    def test_message_de_retour(self):
        reponse = self.lancer_action([e.pk for e in self.exps.values()])
        self.assertContains(reponse, "1 expédition(s) clôturée(s), 4 ignorée(s)")

    def test_fiche_expedition_affiche_les_offres_en_inline(self):
        reponse = self.client.get(f"/admin/ExpeditionsApp/expedition/{self.exps['publiee'].pk}/change/")
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, 'offres-group')
