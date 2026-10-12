from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Entreprise, Utilisateur

# Create your tests here.
def creer_utilisateur(nom, email=None):
    return Utilisateur.objects.create_user(nom, email or f"{nom}@gmail.com", 'motdepasse', telephone='12345678')


class UtilisateurTest(TestCase):
    def test_user_id_suit_le_format_AAuserNN(self):
        aa = f"{timezone.now().year % 100:02d}"
        self.assertEqual(creer_utilisateur('u1').user_id, f"{aa}user00")
        self.assertEqual(creer_utilisateur('u2').user_id, f"{aa}user01")

    def test_compteur_limite_a_99_par_annee(self):
        aa = f"{timezone.now().year % 100:02d}"
        creer_utilisateur('u1')
        Utilisateur.objects.filter(username='u1').update(user_id=f"{aa}user99")
        with self.assertRaises(ValidationError):
            creer_utilisateur('u2')

    def test_email_doit_etre_gmail(self):
        u = Utilisateur(username='x', email='x@yahoo.fr', telephone='12345678')
        with self.assertRaises(ValidationError) as ctx:
            u.clean_fields(exclude=['user_id', 'password'])
        self.assertIn('email', ctx.exception.message_dict)
        Utilisateur(username='y', email='y@gmail.com', telephone='12345678').clean_fields(exclude=['user_id', 'password'])


class EntrepriseTest(TestCase):
    def setUp(self):
        self.compteur = 0

    def entreprise(self, **kwargs):
        self.compteur += 1
        valeurs = dict(raison_sociale='Ste', matricule_fiscal='1234567AAM000', type_entreprise='chargeur',
                       adresse='12 rue de la Liberté, Tunis', gerant=creer_utilisateur(f"g{self.compteur}"))
        valeurs.update(kwargs)
        return Entreprise(**valeurs)

    def test_matricule_formats_acceptes(self):
        for valeur in ['1234567AAM000', '1234567/A/A/M/000', '1234567-A-A-M-000', '1234567 a b p 001']:
            with self.subTest(valeur):
                self.entreprise(matricule_fiscal=valeur).full_clean(exclude=['gerant'])

    def test_matricule_formats_refuses(self):
        for valeur in ['123456AAM000', '1234567AAZ000', '1234567AXM000', '1234567AAM00', 'ABCDEFGAAM000']:
            with self.subTest(valeur):
                with self.assertRaises(ValidationError) as ctx:
                    self.entreprise(matricule_fiscal=valeur).full_clean(exclude=['gerant'])
                self.assertIn('matricule_fiscal', ctx.exception.message_dict)

    def test_matricule_stocke_sans_separateurs(self):
        e = self.entreprise(matricule_fiscal='1234567/a/a/m/000')
        e.save()
        self.assertEqual(Entreprise.objects.get(pk=e.pk).matricule_fiscal, '1234567AAM000')
        with self.assertRaises(ValidationError):
            self.entreprise(matricule_fiscal='1234567-A-A-M-000').save()

    def test_adresse_minimum_20_caracteres(self):
        with self.assertRaises(ValidationError) as ctx:
            self.entreprise(adresse='Tunis centre').full_clean(exclude=['gerant'])
        self.assertIn('adresse', ctx.exception.message_dict)
        self.entreprise(adresse='a' * 20).full_clean(exclude=['gerant'])
