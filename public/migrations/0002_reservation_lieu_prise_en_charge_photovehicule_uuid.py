from django.db import migrations, models
import public.models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0001_initial'),
    ]

    operations = [
        # Ajout du champ lieu_prise_en_charge
        migrations.AddField(
            model_name='reservation',
            name='lieu_prise_en_charge',
            field=models.CharField(default='', max_length=255),
        ),
        # Mise à jour upload_to pour photos véhicule (noms UUID)
        migrations.AlterField(
            model_name='photovehicule',
            name='image',
            field=models.ImageField(upload_to=public.models.upload_vehicule_photo),
        ),
        # Mise à jour upload_to pour CNI recto
        migrations.AlterField(
            model_name='reservation',
            name='cni_recto',
            field=models.ImageField(upload_to=public.models.upload_cni),
        ),
        # Mise à jour upload_to pour CNI verso
        migrations.AlterField(
            model_name='reservation',
            name='cni_verso',
            field=models.ImageField(upload_to=public.models.upload_cni),
        ),
        # Mise à jour upload_to pour permis
        migrations.AlterField(
            model_name='reservation',
            name='permis_conduire',
            field=models.ImageField(upload_to=public.models.upload_permis),
        ),
    ]
