from django.db import models
from django.utils import timezone
import hashlib


class UtilisateurInterne(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('gestionnaire', 'Gestionnaire'),
    ]
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, blank=True)
    photo_profil = models.ImageField(upload_to='profils/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Utilisateur interne'
        verbose_name_plural = 'Utilisateurs internes'
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.role})"

    def set_password(self, raw_password):
        import hashlib
        self.mot_de_passe = hashlib.sha256(raw_password.encode()).hexdigest()

    def check_password(self, raw_password):
        import hashlib
        return self.mot_de_passe == hashlib.sha256(raw_password.encode()).hexdigest()

    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
