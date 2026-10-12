import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VehiculesApp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicule',
            old_name='disponibilite',
            new_name='disponible',
        ),
        migrations.AddField(
            model_name='vehicule',
            name='type_vehicule',
            field=models.CharField(choices=[('camionnette', 'Camionnette / utilitaire léger'), ('camion_porteur', 'Camion porteur'), ('semi_remorque', 'Semi-remorque'), ('fourgon', 'Fourgon')], default='fourgon', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='vehicule',
            name='capacite_kg',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, 'La capacité doit être supérieure à 0')]),
        ),
    ]
