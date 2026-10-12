import EntrepriseApp.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EntrepriseApp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entreprise',
            old_name='matricule_fiscale',
            new_name='matricule_fiscal',
        ),
        migrations.AlterField(
            model_name='entreprise',
            name='matricule_fiscal',
            field=models.CharField(max_length=17, unique=True, validators=[django.core.validators.RegexValidator('^\\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\\d{3}$', 'Matricule fiscal invalide (ex. 1234567AAM000 ou 1234567/A/A/M/000).')]),
        ),
        migrations.AlterField(
            model_name='entreprise',
            name='adresse',
            field=models.TextField(validators=[django.core.validators.MinLengthValidator(20, "L'adresse doit contenir au moins 20 caractères.")]),
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='user_id',
            field=models.CharField(editable=False, max_length=8, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator('^\\d{2}user\\d{2}$', 'Le user_id doit suivre le format AAuserNN.')]),
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='email',
            field=models.EmailField(max_length=254, unique=True, validators=[EntrepriseApp.models.EmailValidate]),
        ),
    ]
