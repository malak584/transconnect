import decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OffresApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offre',
            name='prix',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(decimal.Decimal('0.01'), 'Le prix doit être supérieur à 0')]),
        ),
        migrations.AlterField(
            model_name='offre',
            name='delai_jours',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, "Le délai doit être d'au moins 1 jour")]),
        ),
    ]
