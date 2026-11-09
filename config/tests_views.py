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
    def test_get_affiche_la_confirmation_et_ne_supprime_rien(self):
        for nom, arg in (('expeditions:supprimer', self.expedition.reference),
                         ('vehicules:supprimer', self.vehicule.pk),
                         ('offres:supprimer', self.offre.pk)):
            reponse = self.client.get(reverse(nom, args=[arg]))
            self.assertEqual(reponse.status_code, 200, nom)
            self.assertContains(reponse, 'Oui, supprimer')
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

    def test_la_page_de_confirmation_contient_le_csrf(self):
        reponse = self.client.get(reverse('offres:supprimer', args=[self.offre.pk]))
        self.assertContains(reponse, 'method="post"')
        self.assertContains(reponse, 'csrfmiddlewaretoken')

    def test_le_detail_renvoie_vers_la_confirmation(self):
        reponse = self.client.get(reverse('offres:detail', args=[self.offre.pk]))
        self.assertContains(reponse, reverse('offres:supprimer', args=[self.offre.pk]))


class VehiculeFormTest(DonneesMixin, TestCase):
    def donnees(self, **kwargs):
        valeurs = {'immatriculation': '555TUN5', 'type_vehicule': 'fourgon', 'capacite_kg': 2000, 'entreprise': self.transporteur.pk}
        valeurs.update(kwargs)
        return valeurs

    def test_creation_puis_redirection(self):
        reponse = self.client.post(reverse('vehicules:ajouter'), self.donnees())
        self.assertRedirects(reponse, reverse('vehicules:liste'))
        self.assertTrue(Vehicule.objects.filter(immatriculation='555TUN5').exists())

    def test_actualiser_ne_cree_pas_de_doublon(self):
        self.client.post(reverse('vehicules:ajouter'), self.donnees())
        self.client.get(reverse('vehicules:liste'))
        self.assertEqual(Vehicule.objects.filter(immatriculation='555TUN5').count(), 1)

    def test_immatriculation_deja_utilisee_affiche_une_erreur(self):
        reponse = self.client.post(reverse('vehicules:ajouter'), self.donnees(immatriculation='111TUN1'))
        self.assertEqual(reponse.status_code, 200)
        self.assertTrue(reponse.context['form'].errors)
        self.assertEqual(Vehicule.objects.count(), 1)

    def test_un_chargeur_nest_pas_propose_comme_proprietaire(self):
        reponse = self.client.get(reverse('vehicules:ajouter'))
        self.assertNotIn(self.chargeur, reponse.context['form'].fields['entreprise'].queryset)
        reponse = self.client.post(reverse('vehicules:ajouter'), self.donnees(entreprise=self.chargeur.pk))
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(Vehicule.objects.count(), 1)

    def test_modification(self):
        reponse = self.client.post(reverse('vehicules:modifier', args=[self.vehicule.pk]),
                                   self.donnees(immatriculation='111TUN1', capacite_kg=9000))
        self.assertRedirects(reponse, reverse('vehicules:liste'))
        self.vehicule.refresh_from_db()
        self.assertEqual(self.vehicule.capacite_kg, 9000)

    def test_formulaire_contient_csrf(self):
        reponse = self.client.get(reverse('vehicules:ajouter'))
        self.assertContains(reponse, 'csrfmiddlewaretoken')


class ExpeditionFormTest(DonneesMixin, TestCase):
    def donnees(self, **kwargs):
        valeurs = {'ville_depart': 'Sousse', 'ville_arrivee': 'Gabes', 'date_souhaitee': '2026-12-15',
                   'description': 'Meubles', 'poids_kg': '800'}
        valeurs.update(kwargs)
        return valeurs

    def test_creation_pour_le_chargeur_de_lurl(self):
        reponse = self.client.post(reverse('expeditions:ajouter', args=[self.chargeur.pk]), self.donnees())
        e = Expedition.objects.get(ville_depart='Sousse')
        self.assertRedirects(reponse, reverse('expeditions:detail', args=[e.reference]))
        self.assertEqual(e.entreprise, self.chargeur)
        self.assertEqual(e.statut, 'publiee')

    def test_statut_et_entreprise_ne_viennent_pas_du_client(self):
        self.client.post(reverse('expeditions:ajouter', args=[self.chargeur.pk]),
                         self.donnees(statut='livree', entreprise=self.transporteur.pk, reference='EXP-99-99999'))
        e = Expedition.objects.get(ville_depart='Sousse')
        self.assertEqual(e.statut, 'publiee')
        self.assertEqual(e.entreprise, self.chargeur)
        self.assertNotEqual(e.reference, 'EXP-99-99999')

    def test_un_transporteur_ne_peut_pas_publier(self):
        reponse = self.client.post(reverse('expeditions:ajouter', args=[self.transporteur.pk]), self.donnees())
        self.assertEqual(reponse.status_code, 404)

    def test_poids_negatif_refuse(self):
        reponse = self.client.post(reverse('expeditions:ajouter', args=[self.chargeur.pk]), self.donnees(poids_kg='-5'))
        self.assertEqual(reponse.status_code, 200)
        self.assertIn('poids_kg', reponse.context['form'].errors)

    def test_modification_garde_le_statut(self):
        self.client.post(reverse('expeditions:modifier', args=[self.expedition.reference]),
                         self.donnees(ville_depart='Bizerte', statut='annulee'))
        self.expedition.refresh_from_db()
        self.assertEqual(self.expedition.ville_depart, 'Bizerte')
        self.assertEqual(self.expedition.statut, 'publiee')


class OffreFormTest(DonneesMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.exp_ouverte = cls.nouvelle_expedition()
        cls.autre_transporteur = creer_entreprise('transporteur', 3)
        cls.vehicule_autre = Vehicule.objects.create(immatriculation='999TUN9', type_vehicule='camion_porteur',
                                                    capacite_kg=10000, entreprise=cls.autre_transporteur)

    def url(self):
        return reverse('offres:ajouter', args=[self.transporteur.pk])

    def donnees(self, **kwargs):
        valeurs = {'expedition': self.exp_ouverte.pk, 'vehicule': self.vehicule.pk, 'prix': '700', 'delai_jours': 3}
        valeurs.update(kwargs)
        return valeurs

    def test_le_formulaire_nexpose_ni_statut_ni_transporteur(self):
        reponse = self.client.get(self.url())
        self.assertEqual(set(reponse.context['form'].fields), {'expedition', 'vehicule', 'prix', 'delai_jours'})

    def test_creation_fixe_le_transporteur_et_le_statut(self):
        reponse = self.client.post(self.url(), self.donnees())
        self.assertRedirects(reponse, reverse('expeditions:detail', args=[self.exp_ouverte.reference]))
        offre = Offre.objects.get(expedition=self.exp_ouverte)
        self.assertEqual(offre.transporteur, self.transporteur)
        self.assertEqual(offre.statut, 'proposee')

    def test_statut_acceptee_envoye_par_le_client_est_ignore(self):
        self.client.post(self.url(), self.donnees(statut='acceptee', transporteur=self.autre_transporteur.pk))
        offre = Offre.objects.get(expedition=self.exp_ouverte)
        self.assertEqual(offre.statut, 'proposee')
        self.assertEqual(offre.transporteur, self.transporteur)
        self.exp_ouverte.refresh_from_db()
        self.assertEqual(self.exp_ouverte.statut, 'publiee')

    def test_vehicule_dun_autre_transporteur_refuse(self):
        reponse = self.client.post(self.url(), self.donnees(vehicule=self.vehicule_autre.pk))
        self.assertEqual(reponse.status_code, 200)
        self.assertIn('vehicule', reponse.context['form'].errors)
        self.assertFalse(Offre.objects.filter(expedition=self.exp_ouverte).exists())

    def test_expedition_non_publiee_refusee(self):
        fermee = self.nouvelle_expedition(statut='annulee')
        reponse = self.client.post(self.url(), self.donnees(expedition=fermee.pk))
        self.assertEqual(reponse.status_code, 200)
        self.assertIn('expedition', reponse.context['form'].errors)

    def test_doublon_de_proposition_affiche_une_erreur_et_pas_un_500(self):
        self.client.post(self.url(), self.donnees())
        reponse = self.client.post(self.url(), self.donnees(prix='650'))
        self.assertEqual(reponse.status_code, 200)
        self.assertTrue(reponse.context['form'].non_field_errors())
        self.assertEqual(Offre.objects.filter(expedition=self.exp_ouverte).count(), 1)

    def test_chargeur_ne_peut_pas_proposer(self):
        reponse = self.client.get(reverse('offres:ajouter', args=[self.chargeur.pk]))
        self.assertEqual(reponse.status_code, 404)

    def test_modification_limitee_au_prix_et_au_delai(self):
        reponse = self.client.get(reverse('offres:modifier', args=[self.offre.pk]))
        self.assertEqual(set(reponse.context['form'].fields), {'prix', 'delai_jours'})
        self.client.post(reverse('offres:modifier', args=[self.offre.pk]), {'prix': '500', 'delai_jours': 4, 'statut': 'acceptee'})
        self.offre.refresh_from_db()
        self.assertEqual(self.offre.prix, 500)
        self.assertEqual(self.offre.statut, 'proposee')

    def test_offre_acceptee_non_modifiable(self):
        Offre.objects.filter(pk=self.offre.pk).update(statut='acceptee')
        self.assertEqual(self.client.get(reverse('offres:modifier', args=[self.offre.pk])).status_code, 404)
