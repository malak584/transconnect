import datetime

from django.test import TestCase
from django.urls import reverse

from EntrepriseApp.models import Entreprise, Utilisateur
from ExpeditionsApp.models import Expedition
from OffresApp.models import Offre
from VehiculesApp.models import Vehicule


def creer_entreprise(type_entreprise, n):
    gerant = Utilisateur.objects.create_user(f"g{n}", f"g{n}@gmail.com", 'motdepasse', telephone='12345678')
    return Entreprise.objects.create(raison_sociale=f"Ste {n}", matricule_fiscal=f"123456{n}AAM000", type_entreprise=type_entreprise,
                                     adresse='12 rue de la Liberté, Tunis', gerant=gerant)


class DonneesMixin:
    @classmethod
    def setUpTestData(cls):
        cls.chargeur = creer_entreprise('chargeur', 1)
        cls.transporteur = creer_entreprise('transporteur', 2)
        cls.vehicule = Vehicule.objects.create(immatriculation='111TUN1', type_vehicule='camion_porteur', capacite_kg=10000, entreprise=cls.transporteur)
        cls.expedition = cls.nouvelle_expedition()
        cls.offre = Offre.objects.create(prix=800, delai_jours=2, expedition=cls.expedition, transporteur=cls.transporteur, vehicule=cls.vehicule)

    @classmethod
    def nouvelle_expedition(cls, **kwargs):
        valeurs = dict(ville_depart='Tunis', ville_arrivee='Sfax', date_souhaitee=datetime.date(2026, 12, 1),
                       description='Palettes', poids_kg=500, entreprise=cls.chargeur)
        valeurs.update(kwargs)
        return Expedition.objects.create(**valeurs)


class RoutageTest(DonneesMixin, TestCase):
    def test_pages_de_lecture_repondent_200(self):
        urls = [
            reverse('accueil') + '',
            reverse('expeditions:liste'), reverse('expeditions:detail', args=[self.expedition.reference]),
            reverse('vehicules:liste'), reverse('vehicules:detail', args=[self.vehicule.pk]),
            reverse('offres:liste'), reverse('offres:detail', args=[self.offre.pk]),
            reverse('entreprises:liste'), reverse('entreprises:detail', args=[self.chargeur.pk]),
            reverse('entreprises:detail', args=[self.transporteur.pk]),
        ]
        for url in urls:
            reponse = self.client.get(url, follow=True)
            self.assertEqual(reponse.status_code, 200, url)

    def test_detail_inexistant_renvoie_404(self):
        self.assertEqual(self.client.get(reverse('expeditions:detail', args=['EXP-00-00000'])).status_code, 404)
        self.assertEqual(self.client.get(reverse('vehicules:detail', args=[9999])).status_code, 404)
        self.assertEqual(self.client.get(reverse('offres:detail', args=[9999])).status_code, 404)
        self.assertEqual(self.client.get(reverse('entreprises:detail', args=[9999])).status_code, 404)

    def test_navigation_presente_sur_chaque_page(self):
        reponse = self.client.get(reverse('expeditions:liste'))
        for nom in ('expeditions:liste', 'vehicules:liste', 'offres:liste', 'entreprises:liste'):
            self.assertContains(reponse, f'href="{reverse(nom)}"')


class ListeExpeditionsTest(DonneesMixin, TestCase):
    def test_seules_les_expeditions_publiees_sont_listees(self):
        annulee = self.nouvelle_expedition(statut='annulee')
        reponse = self.client.get(reverse('expeditions:liste'))
        self.assertContains(reponse, self.expedition.reference)
        self.assertNotContains(reponse, annulee.reference)

    def test_message_si_liste_vide(self):
        Expedition.objects.all().delete()
        reponse = self.client.get(reverse('expeditions:liste'))
        self.assertContains(reponse, 'Aucune expédition disponible pour le moment.')

    def test_nombre_de_requetes_constant(self):
        with self.assertNumQueries(1):
            self.client.get(reverse('expeditions:liste'))
        for _ in range(5):
            self.nouvelle_expedition()
        with self.assertNumQueries(1):
            self.client.get(reverse('expeditions:liste'))


class RequetesDeLectureTest(DonneesMixin, TestCase):
    def test_listes_sans_n_plus_1(self):
        for nom in ('vehicules:liste', 'offres:liste', 'entreprises:liste'):
            reponse_vide = self.client.get(reverse(nom))
            self.assertEqual(reponse_vide.status_code, 200)
        v2 = Vehicule.objects.create(immatriculation='222TUN2', type_vehicule='camion_porteur', capacite_kg=10000, entreprise=self.transporteur)
        e2 = self.nouvelle_expedition()
        Offre.objects.create(prix=900, delai_jours=3, expedition=e2, transporteur=self.transporteur, vehicule=v2)
        for nom, attendu in (('vehicules:liste', 1), ('offres:liste', 1), ('entreprises:liste', 1)):
            with self.assertNumQueries(attendu):
                self.client.get(reverse(nom))

    def test_detail_expedition_requetes_fixes(self):
        with self.assertNumQueries(2):
            self.client.get(reverse('expeditions:detail', args=[self.expedition.reference]))


class SuppressionTest(DonneesMixin, TestCase):
    def test_get_refuse_et_ne_supprime_rien(self):
        for nom, arg in (('expeditions:supprimer', self.expedition.reference),
                         ('vehicules:supprimer', self.vehicule.pk),
                         ('offres:supprimer', self.offre.pk)):
            self.assertEqual(self.client.get(reverse(nom, args=[arg])).status_code, 405, nom)
        self.assertTrue(Expedition.objects.filter(pk=self.expedition.pk).exists())
        self.assertTrue(Vehicule.objects.filter(pk=self.vehicule.pk).exists())
        self.assertTrue(Offre.objects.filter(pk=self.offre.pk).exists())

    def test_post_supprime_une_offre_et_redirige(self):
        reponse = self.client.post(reverse('offres:supprimer', args=[self.offre.pk]), follow=True)
        self.assertRedirects(reponse, reverse('offres:liste'))
        self.assertFalse(Offre.objects.filter(pk=self.offre.pk).exists())
        self.assertContains(reponse, 'a été supprimée')

    def test_post_supprime_un_vehicule(self):
        v = Vehicule.objects.create(immatriculation='333TUN3', type_vehicule='fourgon', capacite_kg=3000, entreprise=self.transporteur)
        reponse = self.client.post(reverse('vehicules:supprimer', args=[v.pk]))
        self.assertRedirects(reponse, reverse('vehicules:liste'))
        self.assertFalse(Vehicule.objects.filter(pk=v.pk).exists())

    def test_post_supprime_une_expedition(self):
        reponse = self.client.post(reverse('expeditions:supprimer', args=[self.expedition.reference]))
        self.assertRedirects(reponse, reverse('expeditions:liste'))
        self.assertFalse(Expedition.objects.filter(pk=self.expedition.pk).exists())

    def test_post_sur_objet_inexistant_renvoie_404(self):
        self.assertEqual(self.client.post(reverse('offres:supprimer', args=[9999])).status_code, 404)

    def test_csrf_exige_sur_les_formulaires_de_suppression(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        reponse = client.post(reverse('offres:supprimer', args=[self.offre.pk]))
        self.assertEqual(reponse.status_code, 403)
        self.assertTrue(Offre.objects.filter(pk=self.offre.pk).exists())

    def test_les_pages_de_detail_proposent_un_formulaire_post(self):
        reponse = self.client.get(reverse('offres:detail', args=[self.offre.pk]))
        self.assertContains(reponse, 'method="post"')
        self.assertContains(reponse, 'csrfmiddlewaretoken')
