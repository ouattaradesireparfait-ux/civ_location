from django.core.management.base import BaseCommand
from gestion.models import UtilisateurInterne


class Command(BaseCommand):
    help = "Initialise les comptes administrateurs par défaut"

    def create_admin(self, nom, prenom, email, password):
        if UtilisateurInterne.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(
                f'Un compte avec l\'email {email} existe déjà.'
            ))
        else:
            admin = UtilisateurInterne(
                nom=nom,
                prenom=prenom,
                email=email,
                telephone='',
                role='admin',
                statut='actif',
            )
            admin.set_password(password)
            admin.save()
            self.stdout.write(self.style.SUCCESS(
                f'✅ Compte créé : {email}'
            ))

    def handle(self, *args, **options):
        self.create_admin('Aboudou', 'Franck', 'franckyaboudou@gmail.com', 'AdminDefaut')
        self.create_admin('Ouattara', 'Désiré Parfait', 'ouattaradesireparfait@gmail.com', 'AdminDefaut')