from django.core.management.base import BaseCommand
from gestion.models import UtilisateurInterne


class Command(BaseCommand):
    help = "Initialise le compte administrateur par défaut"

    def handle(self, *args, **options):
        email = 'franckyaboudou@gmail.com'
        if UtilisateurInterne.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(
                f'Un compte administrateur avec l\'email {email} existe déjà.'
            ))
            return

        admin = UtilisateurInterne(
            nom='Aboudou',
            prenom='Franck',
            email=email,
            telephone='',
            role='admin',
            statut='actif',
        )
        admin.set_password('AdminDefaut')
        admin.save()

        self.stdout.write(self.style.SUCCESS(
            f'✅ Compte administrateur créé avec succès !\n'
            f'   Email    : {email}\n'
            f'   Mot de passe : AdminDefaut\n'
            f'   Rôle     : Administrateur'
        ))
