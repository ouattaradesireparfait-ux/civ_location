from django.core.mail import send_mail
from django.conf import settings
from datetime import date as date_type


def _fmt_date(d):
    """Formate une date qu'elle soit un objet date ou une chaîne ISO."""
    if isinstance(d, date_type):
        return d.strftime('%d/%m/%Y')
    try:
        return date_type.fromisoformat(str(d)).strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        return str(d)


def notifier_nouvelle_reservation(reservation):
    """Notifie l'admin par email lors d'une nouvelle réservation."""
    sujet = f"[CIV Location] Nouvelle réservation #{reservation.pk} — {reservation.vehicule.marque} {reservation.vehicule.modele}"
    message = f"""
Bonjour,

Une nouvelle demande de réservation vient d'être soumise sur CIV Location.

━━━━━━━━━━━━━━━━━━━━━━━━━━
INFORMATIONS CLIENT
━━━━━━━━━━━━━━━━━━━━━━━━━━
Nom complet  : {reservation.prenom} {reservation.nom}
Email        : {reservation.email}
Téléphone    : {reservation.telephone}

━━━━━━━━━━━━━━━━━━━━━━━━━━
VÉHICULE DEMANDÉ
━━━━━━━━━━━━━━━━━━━━━━━━━━
Véhicule     : {reservation.vehicule.marque} {reservation.vehicule.modele} {reservation.vehicule.annee}
Agence       : {reservation.vehicule.partenaire.nom_agence}
Localisation : {reservation.vehicule.localisation}
Prix/jour    : {reservation.vehicule.prix_par_jour} FCFA

━━━━━━━━━━━━━━━━━━━━━━━━━━
DATES & LIEU DE PRISE EN CHARGE
━━━━━━━━━━━━━━━━━━━━━━━━━━
Date début   : {_fmt_date(reservation.date_debut)}
Date fin     : {_fmt_date(reservation.date_fin)}
Durée        : {reservation.nombre_jours()} jour(s)
Prix total   : {reservation.prix_total()} FCFA
Paiement     : Cash à la livraison
Lieu prise en charge : {reservation.lieu_prise_en_charge}

━━━━━━━━━━━━━━━━━━━━━━━━━━

Connectez-vous à l'espace de gestion pour traiter cette réservation :
http://127.0.0.1:8000/gestion/reservations/{reservation.pk}/

Référence : #{reservation.pk}

— CIV Location
    """
    try:
        send_mail(
            subject=sujet,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )
    except Exception:
        pass


def notifier_nouvelle_demande_partenaire(demande):
    """Notifie l'admin par email lors d'une nouvelle demande partenaire."""
    sujet = f"[CIV Location] Nouvelle demande partenaire — {demande.nom_agence}"
    message = f"""
Bonjour,

Une nouvelle demande de partenariat vient d'être soumise sur CIV Location.

━━━━━━━━━━━━━━━━━━━━━━━━━━
INFORMATIONS DE L'AGENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━
Agence       : {demande.nom_agence}
Responsable  : {demande.prenom_responsable} {demande.nom_responsable}
Email        : {demande.email}
Téléphone    : {demande.telephone}
Ville        : {demande.ville}
Adresse      : {demande.adresse}
Document     : {'Fourni' if demande.document_justificatif else 'Non fourni'}

━━━━━━━━━━━━━━━━━━━━━━━━━━

Connectez-vous à l'espace de gestion pour valider ou refuser cette demande :
http://127.0.0.1:8000/gestion/partenaires/

— CIV Location
    """
    try:
        send_mail(
            subject=sujet,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )
    except Exception:
        pass
