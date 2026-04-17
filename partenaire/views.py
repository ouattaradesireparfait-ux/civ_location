from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from public.models import Partenaire, Vehicule, PhotoVehicule, Reservation
import hashlib


def login_required_partenaire(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('partenaire_id'):
            return redirect('partenaire_connexion')
        try:
            p = Partenaire.objects.get(pk=request.session['partenaire_id'])
            if p.statut != 'actif':
                request.session.pop('partenaire_id', None)
                return redirect('partenaire_connexion')
            request.partenaire = p
        except Partenaire.DoesNotExist:
            request.session.pop('partenaire_id', None)
            return redirect('partenaire_connexion')
        return view_func(request, *args, **kwargs)
    return wrapper


def connexion(request):
    if request.session.get('partenaire_id'):
        return redirect('partenaire_dashboard')
    erreur = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        mdp = request.POST.get('mot_de_passe', '')
        try:
            p = Partenaire.objects.get(email=email)
            mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
            if p.mot_de_passe == mdp_hash:
                if p.statut == 'en_attente':
                    erreur = "Votre compte est en attente de validation. Revenez plus tard."
                elif p.statut == 'suspendu':
                    erreur = "Votre compte est suspendu. Contactez l'administrateur."
                else:
                    request.session['partenaire_id'] = p.pk
                    p.derniere_connexion = timezone.now()
                    p.save(update_fields=['derniere_connexion'])
                    return redirect('partenaire_dashboard')
            else:
                erreur = "Email ou mot de passe incorrect."
        except Partenaire.DoesNotExist:
            erreur = "Email ou mot de passe incorrect."
    return render(request, 'partenaire/connexion.html', {'erreur': erreur})


def deconnexion(request):
    request.session.pop('partenaire_id', None)
    return redirect('partenaire_connexion')


@login_required_partenaire
def dashboard(request):
    p = request.partenaire
    vehicules_ids = p.vehicules.values_list('id', flat=True)
    stats = {
        'vues': sum(p.vehicules.values_list('vues', flat=True)),
        'reservations': Reservation.objects.filter(vehicule__partenaire=p).count(),
        'vehicules': p.vehicules.count(),
    }
    reservations = Reservation.objects.filter(vehicule__partenaire=p).order_by('-date_demande')[:8]
    vehicules = p.vehicules.all()[:6]
    return render(request, 'partenaire/tableau_de_bord.html', {
        'partenaire': p, 'stats': stats, 'reservations': reservations, 'vehicules': vehicules,
    })


@login_required_partenaire
def annonces(request):
    p = request.partenaire
    vehicules = p.vehicules.all()
    return render(request, 'partenaire/annonces.html', {'partenaire': p, 'vehicules': vehicules})


@login_required_partenaire
def annonce_ajouter(request):
    p = request.partenaire
    erreur = None
    if request.method == 'POST':
        marque = request.POST.get('marque', '').strip()
        modele = request.POST.get('modele', '').strip()
        annee = request.POST.get('annee', '')
        couleur = request.POST.get('couleur', '').strip()
        type_vehicule = request.POST.get('type_vehicule', '')
        nombre_places = request.POST.get('nombre_places', '')
        transmission = request.POST.get('transmission', 'manuelle')
        climatisation = request.POST.get('climatisation', '1') == '1'
        prix_par_jour = request.POST.get('prix_par_jour', '')
        localisation = request.POST.get('localisation', '').strip()
        disponible = request.POST.get('disponible', '1') == '1'
        description = request.POST.get('description', '').strip()
        photos = request.FILES.getlist('photos')

        if not all([marque, modele, annee, couleur, type_vehicule, nombre_places, prix_par_jour, localisation]):
            erreur = "Veuillez remplir tous les champs obligatoires."
        else:
            try:
                v = Vehicule.objects.create(
                    partenaire=p,
                    marque=marque, modele=modele, annee=int(annee), couleur=couleur,
                    type_vehicule=type_vehicule, nombre_places=int(nombre_places),
                    transmission=transmission, climatisation=climatisation,
                    prix_par_jour=float(prix_par_jour), localisation=localisation,
                    disponible=disponible, description=description,
                    statut_validation='en_attente',
                )
                for i, photo in enumerate(photos):
                    PhotoVehicule.objects.create(vehicule=v, image=photo, ordre=i)
                messages.success(request, "Véhicule soumis avec succès. Il sera visible après validation.")
                return redirect('partenaire_annonces')
            except (ValueError, TypeError):
                erreur = "Données invalides. Vérifiez les champs numériques."

    return render(request, 'partenaire/annonce_form.html', {
        'partenaire': p, 'types': Vehicule.TYPE_CHOICES, 'erreur': erreur,
    })


@login_required_partenaire
def annonce_modifier(request, pk):
    p = request.partenaire
    v = get_object_or_404(Vehicule, pk=pk, partenaire=p)
    erreur = None
    if request.method == 'POST':
        v.marque = request.POST.get('marque', v.marque).strip()
        v.modele = request.POST.get('modele', v.modele).strip()
        v.couleur = request.POST.get('couleur', v.couleur).strip()
        v.localisation = request.POST.get('localisation', v.localisation).strip()
        v.description = request.POST.get('description', '').strip()
        v.type_vehicule = request.POST.get('type_vehicule', v.type_vehicule)
        v.transmission = request.POST.get('transmission', v.transmission)
        v.climatisation = request.POST.get('climatisation', '1') == '1'
        v.disponible = request.POST.get('disponible', '1') == '1'
        try:
            v.annee = int(request.POST.get('annee', v.annee))
            v.nombre_places = int(request.POST.get('nombre_places', v.nombre_places))
            v.prix_par_jour = float(request.POST.get('prix_par_jour', v.prix_par_jour))
            v.statut_validation = 'en_attente'  # Repassera en validation
            photos = request.FILES.getlist('photos')
            v.save()
            if photos:
                v.photos.all().delete()
                for i, photo in enumerate(photos):
                    PhotoVehicule.objects.create(vehicule=v, image=photo, ordre=i)
            messages.success(request, "Annonce modifiée. Repassée en attente de validation.")
            return redirect('partenaire_annonces')
        except (ValueError, TypeError):
            erreur = "Données invalides."
    return render(request, 'partenaire/annonce_form.html', {
        'partenaire': p, 'vehicule': v, 'types': Vehicule.TYPE_CHOICES, 'erreur': erreur,
    })


@login_required_partenaire
def annonce_supprimer(request, pk):
    p = request.partenaire
    v = get_object_or_404(Vehicule, pk=pk, partenaire=p)
    nom = f"{v.marque} {v.modele}"
    v.delete()
    messages.success(request, f"Annonce {nom} supprimée.")
    return redirect('partenaire_annonces')


@login_required_partenaire
def reservations(request):
    p = request.partenaire
    qs = Reservation.objects.filter(vehicule__partenaire=p).select_related('vehicule').order_by('-date_demande')
    return render(request, 'partenaire/reservations.html', {'partenaire': p, 'reservations': qs})


@login_required_partenaire
def profil(request):
    p = request.partenaire
    erreur = None
    if request.method == 'POST':
        p.nom_agence = request.POST.get('nom_agence', p.nom_agence).strip()
        p.prenom_responsable = request.POST.get('prenom_responsable', p.prenom_responsable).strip()
        p.nom_responsable = request.POST.get('nom_responsable', p.nom_responsable).strip()
        new_email = request.POST.get('email', p.email).strip()
        p.telephone = request.POST.get('telephone', p.telephone).strip()
        p.adresse = request.POST.get('adresse', p.adresse).strip()
        p.ville = request.POST.get('ville', p.ville).strip()
        mdp = request.POST.get('mot_de_passe', '')
        logo = request.FILES.get('logo')
        if Partenaire.objects.filter(email=new_email).exclude(pk=p.pk).exists():
            erreur = "Cet email est déjà utilisé."
        else:
            p.email = new_email
            if mdp:
                p.mot_de_passe = hashlib.sha256(mdp.encode()).hexdigest()
            if logo:
                p.logo = logo
            p.save()
            messages.success(request, "Profil mis à jour.")
            return redirect('partenaire_profil')
    return render(request, 'partenaire/profil.html', {'partenaire': p, 'erreur': erreur})
