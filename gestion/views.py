from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from gestion.models import UtilisateurInterne
from public.models import Partenaire, Vehicule, Reservation, DemandePartenaire


def login_required_interne(view_func):
    """Décorateur maison pour l'espace gestion"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('utilisateur_id'):
            return redirect('gestion_connexion')
        try:
            u = UtilisateurInterne.objects.get(pk=request.session['utilisateur_id'])
            if u.statut == 'suspendu':
                request.session.flush()
                return redirect('gestion_connexion')
            request.utilisateur = u
        except UtilisateurInterne.DoesNotExist:
            request.session.flush()
            return redirect('gestion_connexion')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('utilisateur_id'):
            return redirect('gestion_connexion')
        try:
            u = UtilisateurInterne.objects.get(pk=request.session['utilisateur_id'])
            if u.statut == 'suspendu' or u.role != 'admin':
                return redirect('gestion_connexion')
            request.utilisateur = u
        except UtilisateurInterne.DoesNotExist:
            request.session.flush()
            return redirect('gestion_connexion')
        return view_func(request, *args, **kwargs)
    return wrapper


def connexion(request):
    if request.session.get('utilisateur_id'):
        return _redirect_by_role(request)
    erreur = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        mdp = request.POST.get('mot_de_passe', '')
        try:
            u = UtilisateurInterne.objects.get(email=email)
            if u.check_password(mdp):
                if u.statut == 'suspendu':
                    erreur = "Votre compte est suspendu. Contactez un administrateur."
                else:
                    request.session['utilisateur_id'] = u.pk
                    u.derniere_connexion = timezone.now()
                    u.save(update_fields=['derniere_connexion'])
                    return _redirect_by_role(request)
            else:
                erreur = "Email ou mot de passe incorrect."
        except UtilisateurInterne.DoesNotExist:
            erreur = "Email ou mot de passe incorrect."
    return render(request, 'gestion/connexion.html', {'erreur': erreur})


def _redirect_by_role(request):
    uid = request.session.get('utilisateur_id')
    try:
        u = UtilisateurInterne.objects.get(pk=uid)
        if u.role == 'admin':
            return redirect('gestion_admin_dashboard')
        return redirect('gestion_gestionnaire_dashboard')
    except Exception:
        return redirect('gestion_connexion')


def deconnexion(request):
    request.session.flush()
    return redirect('gestion_connexion')


def _get_utilisateur(request):
    return UtilisateurInterne.objects.get(pk=request.session['utilisateur_id'])


@login_required_interne
def admin_dashboard(request):
    u = request.utilisateur
    if u.role != 'admin':
        return redirect('gestion_gestionnaire_dashboard')
    stats = {
        'reservations': Reservation.objects.count(),
        'partenaires': Partenaire.objects.filter(statut='actif').count(),
        'vehicules': Vehicule.objects.filter(statut_validation='valide').count(),
        'gestionnaires': UtilisateurInterne.objects.filter(role='gestionnaire').count(),
    }
    return render(request, 'gestion/admin/tableau_de_bord.html', {
        'utilisateur': u,
        'stats': stats,
        'reservations_recentes': Reservation.objects.order_by('-date_demande')[:8],
        'partenaires_attente': DemandePartenaire.objects.filter(traitee=False).order_by('-date_demande')[:5],
    })


@login_required_interne
def gestionnaire_dashboard(request):
    u = request.utilisateur
    if u.role != 'gestionnaire':
        return redirect('gestion_admin_dashboard')
    reservations_attente = Reservation.objects.filter(statut='en_attente')
    annonces_attente = Vehicule.objects.filter(statut_validation='en_attente')
    return render(request, 'gestion/gestionnaire/tableau_de_bord.html', {
        'utilisateur': u,
        'stats': {
            'reservations_attente': reservations_attente.count(),
            'annonces_attente': annonces_attente.count(),
            'reservations_total': Reservation.objects.count(),
        },
        'reservations_attente': reservations_attente[:8],
        'annonces_attente': annonces_attente[:8],
    })


# ---- GESTIONNAIRES ----

@admin_required
def gestionnaires(request):
    u = request.utilisateur
    return render(request, 'gestion/admin/gestionnaires.html', {
        'utilisateur': u,
        'gestionnaires': UtilisateurInterne.objects.filter(role='gestionnaire'),
    })


@admin_required
def gestionnaire_creer(request):
    u = request.utilisateur
    erreur = None
    if request.method == 'POST':
        prenom = request.POST.get('prenom', '').strip()
        nom = request.POST.get('nom', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        mdp = request.POST.get('mot_de_passe', '')
        photo = request.FILES.get('photo_profil')
        if not all([prenom, nom, email, mdp]):
            erreur = "Veuillez remplir tous les champs obligatoires."
        elif UtilisateurInterne.objects.filter(email=email).exists():
            erreur = "Un compte avec cet email existe déjà."
        else:
            g = UtilisateurInterne(prenom=prenom, nom=nom, email=email, telephone=telephone, role='gestionnaire')
            g.set_password(mdp)
            if photo:
                g.photo_profil = photo
            g.save()
            messages.success(request, f"Gestionnaire {prenom} {nom} créé avec succès.")
            return redirect('gestion_gestionnaires')
    return render(request, 'gestion/admin/gestionnaire_form.html', {'utilisateur': u, 'erreur': erreur})


@admin_required
def gestionnaire_modifier(request, pk):
    u = request.utilisateur
    g = get_object_or_404(UtilisateurInterne, pk=pk, role='gestionnaire')
    erreur = None
    if request.method == 'POST':
        g.prenom = request.POST.get('prenom', g.prenom).strip()
        g.nom = request.POST.get('nom', g.nom).strip()
        new_email = request.POST.get('email', g.email).strip()
        g.telephone = request.POST.get('telephone', '').strip()
        mdp = request.POST.get('mot_de_passe', '')
        photo = request.FILES.get('photo_profil')
        if UtilisateurInterne.objects.filter(email=new_email).exclude(pk=g.pk).exists():
            erreur = "Cet email est déjà utilisé."
        else:
            g.email = new_email
            if mdp:
                g.set_password(mdp)
            if photo:
                g.photo_profil = photo
            g.save()
            messages.success(request, "Gestionnaire mis à jour.")
            return redirect('gestion_gestionnaires')
    return render(request, 'gestion/admin/gestionnaire_form.html', {'utilisateur': u, 'gestionnaire': g, 'erreur': erreur})


@admin_required
def gestionnaire_statut(request, pk):
    g = get_object_or_404(UtilisateurInterne, pk=pk, role='gestionnaire')
    g.statut = 'suspendu' if g.statut == 'actif' else 'actif'
    g.save()
    messages.success(request, f"Statut de {g.prenom} {g.nom} mis à jour.")
    return redirect('gestion_gestionnaires')


@admin_required
def gestionnaire_supprimer(request, pk):
    g = get_object_or_404(UtilisateurInterne, pk=pk, role='gestionnaire')
    nom = f"{g.prenom} {g.nom}"
    g.delete()
    messages.success(request, f"Gestionnaire {nom} supprimé définitivement.")
    return redirect('gestion_gestionnaires')


# ---- PARTENAIRES ----

@admin_required
def partenaires(request):
    u = request.utilisateur
    statut_filtre = request.GET.get('statut', '')
    qs = Partenaire.objects.all()
    if statut_filtre:
        qs = qs.filter(statut=statut_filtre)
    return render(request, 'gestion/admin/partenaires.html', {
        'utilisateur': u, 'partenaires': qs, 'statut_filtre': statut_filtre,
    })


@admin_required
def partenaire_detail(request, pk):
    u = request.utilisateur
    p = get_object_or_404(Partenaire, pk=pk)
    return render(request, 'gestion/admin/partenaire_detail.html', {'utilisateur': u, 'partenaire': p})


@admin_required
def partenaire_creer(request):
    u = request.utilisateur
    erreur = None
    if request.method == 'POST':
        nom_agence = request.POST.get('nom_agence', '').strip()
        prenom = request.POST.get('prenom_responsable', '').strip()
        nom = request.POST.get('nom_responsable', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        ville = request.POST.get('ville', '').strip()
        mdp = request.POST.get('mot_de_passe', '')
        if not all([nom_agence, prenom, nom, email, telephone, adresse, ville, mdp]):
            erreur = "Veuillez remplir tous les champs obligatoires."
        elif Partenaire.objects.filter(email=email).exists():
            erreur = "Un partenaire avec cet email existe déjà."
        else:
            import hashlib
            p = Partenaire(
                nom_agence=nom_agence, nom_responsable=nom, prenom_responsable=prenom,
                email=email, telephone=telephone, adresse=adresse, ville=ville,
                statut='actif',
            )
            p.mot_de_passe = hashlib.sha256(mdp.encode()).hexdigest()
            if request.FILES.get('logo'):
                p.logo = request.FILES['logo']
            if request.FILES.get('document_justificatif'):
                p.document_justificatif = request.FILES['document_justificatif']
            p.save()
            messages.success(request, f"Partenaire {nom_agence} créé avec succès.")
            return redirect('gestion_partenaires')
    return render(request, 'gestion/admin/partenaire_form.html', {'utilisateur': u, 'erreur': erreur})


@admin_required
def partenaire_modifier(request, pk):
    u = request.utilisateur
    p = get_object_or_404(Partenaire, pk=pk)
    erreur = None
    if request.method == 'POST':
        import hashlib
        p.nom_agence = request.POST.get('nom_agence', p.nom_agence).strip()
        p.prenom_responsable = request.POST.get('prenom_responsable', p.prenom_responsable).strip()
        p.nom_responsable = request.POST.get('nom_responsable', p.nom_responsable).strip()
        new_email = request.POST.get('email', p.email).strip()
        p.telephone = request.POST.get('telephone', p.telephone).strip()
        p.adresse = request.POST.get('adresse', p.adresse).strip()
        p.ville = request.POST.get('ville', p.ville).strip()
        p.statut = request.POST.get('statut', p.statut)
        mdp = request.POST.get('mot_de_passe', '')
        if Partenaire.objects.filter(email=new_email).exclude(pk=p.pk).exists():
            erreur = "Cet email est déjà utilisé."
        else:
            p.email = new_email
            if mdp:
                p.mot_de_passe = hashlib.sha256(mdp.encode()).hexdigest()
            if request.FILES.get('logo'):
                p.logo = request.FILES['logo']
            if request.FILES.get('document_justificatif'):
                p.document_justificatif = request.FILES['document_justificatif']
            p.save()
            messages.success(request, "Partenaire mis à jour.")
            return redirect('gestion_partenaires')
    return render(request, 'gestion/admin/partenaire_form.html', {'utilisateur': u, 'partenaire': p, 'erreur': erreur})


@admin_required
def partenaire_statut(request, pk, statut):
    p = get_object_or_404(Partenaire, pk=pk)
    if statut in ['actif', 'suspendu', 'en_attente']:
        p.statut = statut
        p.save()
        messages.success(request, f"Statut de {p.nom_agence} mis à jour : {p.get_statut_display()}.")
    return redirect('gestion_partenaire_detail', pk=pk)


@admin_required
def partenaire_supprimer(request, pk):
    p = get_object_or_404(Partenaire, pk=pk)
    nom = p.nom_agence
    p.delete()
    messages.success(request, f"Partenaire {nom} supprimé définitivement.")
    return redirect('gestion_partenaires')


# ---- RÉSERVATIONS ----

@login_required_interne
def reservations(request):
    u = request.utilisateur
    statut_filtre = request.GET.get('statut', '')
    q = request.GET.get('q', '')
    qs = Reservation.objects.select_related('vehicule', 'vehicule__partenaire')
    if statut_filtre:
        qs = qs.filter(statut=statut_filtre)
    if q:
        qs = qs.filter(Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(email__icontains=q) | Q(telephone__icontains=q))
    return render(request, 'gestion/reservations.html', {
        'utilisateur': u, 'reservations': qs, 'statut_filtre': statut_filtre, 'q': q,
    })


@login_required_interne
def reservation_detail(request, pk):
    u = request.utilisateur
    r = get_object_or_404(Reservation, pk=pk)
    return render(request, 'gestion/reservation_detail.html', {'utilisateur': u, 'reservation': r})


@login_required_interne
def reservation_valider(request, pk):
    if request.method == 'POST':
        r = get_object_or_404(Reservation, pk=pk)
        r.statut = 'validee'
        r.save()
        messages.success(request, f"Réservation #{pk} validée.")
    return redirect('gestion_reservation_detail', pk=pk)


@login_required_interne
def reservation_refuser(request, pk):
    if request.method == 'POST':
        r = get_object_or_404(Reservation, pk=pk)
        motif = request.POST.get('motif_refus', '').strip()
        r.statut = 'refusee'
        r.motif_refus = motif
        r.save()
        messages.success(request, f"Réservation #{pk} refusée.")
    return redirect('gestion_reservation_detail', pk=pk)


# ---- ANNONCES ----

@login_required_interne
def annonces(request):
    u = request.utilisateur
    statut_filtre = request.GET.get('statut', '')
    qs = Vehicule.objects.select_related('partenaire')
    if statut_filtre:
        qs = qs.filter(statut_validation=statut_filtre)
    return render(request, 'gestion/annonces.html', {
        'utilisateur': u, 'vehicules': qs, 'statut_filtre': statut_filtre,
    })


@login_required_interne
def annonce_detail(request, pk):
    u = request.utilisateur
    v = get_object_or_404(Vehicule, pk=pk)
    return render(request, 'gestion/annonce_detail.html', {'utilisateur': u, 'vehicule': v})


@login_required_interne
def annonce_valider(request, pk):
    if request.method == 'POST':
        v = get_object_or_404(Vehicule, pk=pk)
        v.statut_validation = 'valide'
        v.save()
        messages.success(request, f"Annonce validée : {v.marque} {v.modele}.")
    return redirect('gestion_annonce_detail', pk=pk)


@login_required_interne
def annonce_rejeter(request, pk):
    if request.method == 'POST':
        v = get_object_or_404(Vehicule, pk=pk)
        v.statut_validation = 'rejete'
        v.save()
        messages.success(request, f"Annonce rejetée : {v.marque} {v.modele}.")
    return redirect('gestion_annonce_detail', pk=pk)


# ---- PROFIL ----

@login_required_interne
def profil(request):
    u = request.utilisateur
    erreur = None
    if request.method == 'POST':
        u.prenom = request.POST.get('prenom', u.prenom).strip()
        u.nom = request.POST.get('nom', u.nom).strip()
        new_email = request.POST.get('email', u.email).strip()
        u.telephone = request.POST.get('telephone', '').strip()
        mdp = request.POST.get('mot_de_passe', '')
        photo = request.FILES.get('photo_profil')
        if UtilisateurInterne.objects.filter(email=new_email).exclude(pk=u.pk).exists():
            erreur = "Cet email est déjà utilisé."
        else:
            u.email = new_email
            if mdp:
                u.set_password(mdp)
            if photo:
                u.photo_profil = photo
            u.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('gestion_profil')
    return render(request, 'gestion/profil.html', {'utilisateur': u, 'erreur': erreur})


# ---- DEMANDES PARTENAIRES (formulaire public) ----

@admin_required
def demandes_partenaires(request):
    u = request.utilisateur
    demandes = DemandePartenaire.objects.filter(traitee=False).order_by('-date_demande')
    traitees = DemandePartenaire.objects.filter(traitee=True).order_by('-date_demande')[:10]
    return render(request, 'gestion/admin/demandes_partenaires.html', {
        'utilisateur': u, 'demandes': demandes, 'traitees': traitees,
    })


@admin_required
def demande_partenaire_valider(request, pk):
    """Convertit une DemandePartenaire en vrai compte Partenaire actif."""
    import hashlib, secrets
    demande = get_object_or_404(DemandePartenaire, pk=pk)

    if Partenaire.objects.filter(email=demande.email).exists():
        messages.error(request, f"Un partenaire avec l'email {demande.email} existe déjà.")
        return redirect('gestion_demandes_partenaires')

    # Générer un mot de passe temporaire
    mdp_temp = secrets.token_urlsafe(10)
    mdp_hash = hashlib.sha256(mdp_temp.encode()).hexdigest()

    partenaire = Partenaire.objects.create(
        nom_agence=demande.nom_agence,
        nom_responsable=demande.nom_responsable,
        prenom_responsable=demande.prenom_responsable,
        email=demande.email,
        telephone=demande.telephone,
        adresse=demande.adresse,
        ville=demande.ville,
        document_justificatif=demande.document_justificatif,
        mot_de_passe=mdp_hash,
        statut='actif',
    )

    # Notifier par email
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        send_mail(
            subject="[CIV Location] Votre demande de partenariat a été acceptée",
            message=f"""Bonjour {demande.prenom_responsable} {demande.nom_responsable},

Félicitations ! Votre demande de partenariat pour l'agence "{demande.nom_agence}" a été acceptée.

Vos identifiants de connexion :
  Email       : {demande.email}
  Mot de passe temporaire : {mdp_temp}

Connectez-vous dès maintenant :
http://127.0.0.1:8000/partenaire/connexion/

Pensez à changer votre mot de passe après la première connexion.

— CIV Location""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[demande.email],
            fail_silently=True,
        )
    except Exception:
        pass

    demande.traitee = True
    demande.save()
    messages.success(request, f"Demande acceptée. Compte partenaire créé pour {demande.nom_agence}. Mot de passe temporaire : {mdp_temp}")
    return redirect('gestion_demandes_partenaires')


@admin_required
def demande_partenaire_refuser(request, pk):
    demande = get_object_or_404(DemandePartenaire, pk=pk)
    demande.traitee = True
    demande.save()

    from django.core.mail import send_mail
    from django.conf import settings
    try:
        send_mail(
            subject="[CIV Location] Votre demande de partenariat",
            message=f"""Bonjour {demande.prenom_responsable} {demande.nom_responsable},

Nous avons bien reçu votre demande de partenariat pour l'agence "{demande.nom_agence}".

Après examen, nous ne sommes pas en mesure de donner suite à votre demande pour le moment.

N'hésitez pas à nous contacter pour plus d'informations :
  Email : franckyaboudou@gmail.com
  Tél   : +225 07 89 92 36 11

— CIV Location""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[demande.email],
            fail_silently=True,
        )
    except Exception:
        pass

    messages.success(request, f"Demande de {demande.nom_agence} refusée.")
    return redirect('gestion_demandes_partenaires')
