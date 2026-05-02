from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Vehicule, Reservation, Partenaire, DemandePartenaire
from .emails import notifier_nouvelle_reservation, notifier_nouvelle_demande_partenaire


def accueil(request):
    vehicules = Vehicule.objects.filter(statut_validation='valide', disponible=True)
    type_filtre = request.GET.get('type', '')
    prix_max = request.GET.get('prix_max', '')
    localisation = request.GET.get('localisation', '')
    if type_filtre:
        vehicules = vehicules.filter(type_vehicule=type_filtre)
    if prix_max:
        try:
            vehicules = vehicules.filter(prix_par_jour__lte=float(prix_max))
        except ValueError:
            pass
    if localisation:
        vehicules = vehicules.filter(localisation__icontains=localisation)
    types = Vehicule.TYPE_CHOICES
    localisations = Vehicule.objects.filter(statut_validation='valide').values_list('localisation', flat=True).distinct()
    return render(request, 'public/accueil.html', {
        'vehicules': vehicules, 'types': types, 'localisations': localisations,
        'type_filtre': type_filtre, 'prix_max': prix_max, 'localisation': localisation,
    })


def detail_vehicule(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk, statut_validation='valide')
    vehicule.vues += 1
    vehicule.save(update_fields=['vues'])
    return render(request, 'public/detail_vehicule.html', {
        'vehicule': vehicule, 'photos': vehicule.photos.all(),
    })


def reservation(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk, statut_validation='valide', disponible=True)
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        lieu_prise_en_charge = request.POST.get('lieu_prise_en_charge', '').strip()
        cni_recto = request.FILES.get('cni_recto')
        cni_verso = request.FILES.get('cni_verso')
        permis_conduire = request.FILES.get('permis_conduire')
        erreurs = []
        if not all([nom, prenom, email, telephone, date_debut, date_fin, lieu_prise_en_charge]):
            erreurs.append("Veuillez remplir tous les champs obligatoires.")
        if not cni_recto:
            erreurs.append("La photo CNI recto est obligatoire.")
        if not cni_verso:
            erreurs.append("La photo CNI verso est obligatoire.")
        if not permis_conduire:
            erreurs.append("La photo du permis de conduire est obligatoire.")
        if not erreurs:
            from datetime import date
            try:
                d_debut = date.fromisoformat(date_debut)
                d_fin = date.fromisoformat(date_fin)
                if d_fin < d_debut:
                    erreurs.append("La date de fin doit être après la date de début.")
                if d_debut < date.today():
                    erreurs.append("La date de début ne peut pas être dans le passé.")
            except ValueError:
                erreurs.append("Dates invalides.")
        if not erreurs:
            resa = Reservation.objects.create(
                nom=nom, prenom=prenom, email=email, telephone=telephone,
                vehicule=vehicule, date_debut=date_debut, date_fin=date_fin,
                lieu_prise_en_charge=lieu_prise_en_charge,
                moyen_paiement='cash_livraison',
                cni_recto=cni_recto, cni_verso=cni_verso, permis_conduire=permis_conduire,
            )
            notifier_nouvelle_reservation(resa)
            return render(request, 'public/reservation_succes.html', {'reservation': resa, 'vehicule': vehicule})
        return render(request, 'public/reservation.html', {'vehicule': vehicule, 'erreurs': erreurs, 'post': request.POST})
    return render(request, 'public/reservation.html', {'vehicule': vehicule, 'post': {}})


def suivi_reservation(request):
    reservations = []
    recherche = ''
    if request.method == 'POST':
        recherche = request.POST.get('recherche', '').strip()
        if recherche:
            reservations = Reservation.objects.filter(
                Q(email__iexact=recherche) | Q(telephone=recherche)
            ).order_by('-date_demande')
    return render(request, 'public/suivi_reservation.html', {'reservations': reservations, 'recherche': recherche})


def devenir_partenaire(request):
    if request.method == 'POST':
        nom_agence = request.POST.get('nom_agence', '').strip()
        nom_responsable = request.POST.get('nom_responsable', '').strip()
        prenom_responsable = request.POST.get('prenom_responsable', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        ville = request.POST.get('ville', '').strip()
        document = request.FILES.get('document_justificatif')
        erreurs = []
        if not all([nom_agence, nom_responsable, prenom_responsable, email, telephone, adresse, ville]):
            erreurs.append("Veuillez remplir tous les champs obligatoires.")
        if Partenaire.objects.filter(email=email).exists() or \
           DemandePartenaire.objects.filter(email=email, traitee=False).exists():
            erreurs.append("Une demande avec cet email existe déjà.")
        if not erreurs:
            demande = DemandePartenaire.objects.create(
                nom_agence=nom_agence, nom_responsable=nom_responsable,
                prenom_responsable=prenom_responsable, email=email,
                telephone=telephone, adresse=adresse, ville=ville,
                document_justificatif=document,
            )
            notifier_nouvelle_demande_partenaire(demande)
            return render(request, 'public/demande_succes.html', {})
        return render(request, 'public/devenir_partenaire.html', {'erreurs': erreurs, 'post': request.POST})
    return render(request, 'public/devenir_partenaire.html', {'post': {}})
