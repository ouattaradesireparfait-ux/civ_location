from django.db import models
from django.utils import timezone
import uuid, os


def upload_vehicule_photo(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f'vehicules/photos/{uuid.uuid4().hex}{ext}'


def upload_cni(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f'reservations/cni/{uuid.uuid4().hex}{ext}'


def upload_permis(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f'reservations/permis/{uuid.uuid4().hex}{ext}'


class Partenaire(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
    ]
    nom_agence = models.CharField(max_length=200)
    nom_responsable = models.CharField(max_length=100)
    prenom_responsable = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='partenaires/logos/', blank=True, null=True)
    document_justificatif = models.FileField(upload_to='partenaires/documents/', blank=True, null=True)
    mot_de_passe = models.CharField(max_length=255)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_inscription = models.DateTimeField(default=timezone.now)
    derniere_connexion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Partenaire'
        verbose_name_plural = 'Partenaires'
        ordering = ['-date_inscription']

    def __str__(self):
        return self.nom_agence


class Vehicule(models.Model):
    TYPE_CHOICES = [
        ('berline', 'Berline'),
        ('suv', 'SUV'),
        ('pickup', 'Pick-up'),
        ('minibus', 'Minibus'),
        ('citadine', 'Citadine'),
        ('utilitaire', 'Utilitaire'),
        ('4x4', '4x4'),
        ('van', 'Van'),
    ]
    TRANSMISSION_CHOICES = [
        ('manuelle', 'Manuelle'),
        ('automatique', 'Automatique'),
    ]
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]

    partenaire = models.ForeignKey(Partenaire, on_delete=models.CASCADE, related_name='vehicules')
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    annee = models.PositiveIntegerField()
    type_vehicule = models.CharField(max_length=20, choices=TYPE_CHOICES)
    couleur = models.CharField(max_length=50)
    nombre_places = models.PositiveIntegerField()
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    climatisation = models.BooleanField(default=True)
    prix_par_jour = models.DecimalField(max_digits=10, decimal_places=0)
    localisation = models.CharField(max_length=200)
    disponible = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    statut_validation = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_ajout = models.DateTimeField(default=timezone.now)
    vues = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Véhicule'
        verbose_name_plural = 'Véhicules'
        ordering = ['-date_ajout']

    def __str__(self):
        return f"{self.marque} {self.modele} ({self.annee})"

    def photo_principale(self):
        photo = self.photos.first()
        return photo if photo else None


class PhotoVehicule(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to=upload_vehicule_photo)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return f"Photo {self.ordre} - {self.vehicule}"


class Reservation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
        ('annulee', 'Annulée'),
    ]
    PAIEMENT_CHOICES = [
        ('cash_livraison', 'Cash à la livraison'),
    ]

    # Infos client
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)

    # Véhicule
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='reservations')

    # Dates
    date_debut = models.DateField()
    date_fin = models.DateField()

    # Lieu de prise en charge
    lieu_prise_en_charge = models.CharField(max_length=255, default='')

    # Paiement
    moyen_paiement = models.CharField(max_length=30, choices=PAIEMENT_CHOICES, default='cash_livraison')

    # Documents
    cni_recto = models.ImageField(upload_to=upload_cni)
    cni_verso = models.ImageField(upload_to=upload_cni)
    permis_conduire = models.ImageField(upload_to=upload_permis)

    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    motif_refus = models.TextField(blank=True, help_text="Visible uniquement en interne")
    date_demande = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'
        ordering = ['-date_demande']

    def __str__(self):
        return f"Réservation #{self.pk} - {self.prenom} {self.nom}"

    def _as_date(self, val):
        from datetime import date
        if isinstance(val, date):
            return val
        return date.fromisoformat(str(val))

    def nombre_jours(self):
        delta = self._as_date(self.date_fin) - self._as_date(self.date_debut)
        return delta.days + 1

    def prix_total(self):
        return self.vehicule.prix_par_jour * self.nombre_jours()


class DemandePartenaire(models.Model):
    """Formulaire d'inscription partenaire depuis le site public"""
    nom_agence = models.CharField(max_length=200)
    nom_responsable = models.CharField(max_length=100)
    prenom_responsable = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    document_justificatif = models.FileField(upload_to='demandes/documents/', blank=True, null=True)
    date_demande = models.DateTimeField(default=timezone.now)
    traitee = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Demande partenaire'
        ordering = ['-date_demande']

    def __str__(self):
        return f"Demande - {self.nom_agence}"