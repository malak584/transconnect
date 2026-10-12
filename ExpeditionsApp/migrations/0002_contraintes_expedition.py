import decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ExpeditionsApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expedition',
            name='reference',
            field=models.CharField(editable=False, max_length=12, unique=True, validators=[django.core.validators.RegexValidator('^EXP-\\d{2}-\\d{5}$', 'La référence doit suivre le format EXP-AA-NNNNN.')]),
        ),
        migrations.AlterField(
            model_name='expedition',
            name='poids_kg',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(decimal.Decimal('0.01'), 'Le poids doit être supérieur à 0')]),
        ),
    ]
