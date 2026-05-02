from django.urls import path
from . import views

urlpatterns = [
    path('connexion/', views.connexion, name='gestion_connexion'),
    path('deconnexion/', views.deconnexion, name='gestion_deconnexion'),

    # Admin
    path('admin/tableau-de-bord/', views.admin_dashboard, name='gestion_admin_dashboard'),

    # Gestionnaires
    path('gestionnaires/', views.gestionnaires, name='gestion_gestionnaires'),
    path('gestionnaires/creer/', views.gestionnaire_creer, name='gestion_gestionnaire_creer'),
    path('gestionnaires/<int:pk>/modifier/', views.gestionnaire_modifier, name='gestion_gestionnaire_modifier'),
    path('gestionnaires/<int:pk>/statut/', views.gestionnaire_statut, name='gestion_gestionnaire_statut'),
    path('gestionnaires/<int:pk>/supprimer/', views.gestionnaire_supprimer, name='gestion_gestionnaire_supprimer'),

    # Partenaires
    path('partenaires/', views.partenaires, name='gestion_partenaires'),
    path('partenaires/creer/', views.partenaire_creer, name='gestion_partenaire_creer'),
    path('partenaires/<int:pk>/', views.partenaire_detail, name='gestion_partenaire_detail'),
    path('partenaires/<int:pk>/modifier/', views.partenaire_modifier, name='gestion_partenaire_modifier'),
    path('partenaires/<int:pk>/statut/<str:statut>/', views.partenaire_statut, name='gestion_partenaire_statut'),
    path('partenaires/<int:pk>/supprimer/', views.partenaire_supprimer, name='gestion_partenaire_supprimer'),

    # Réservations
    path('reservations/', views.reservations, name='gestion_reservations'),
    path('reservations/<int:pk>/', views.reservation_detail, name='gestion_reservation_detail'),
    path('reservations/<int:pk>/valider/', views.reservation_valider, name='gestion_reservation_valider'),
    path('reservations/<int:pk>/refuser/', views.reservation_refuser, name='gestion_reservation_refuser'),

    # Annonces
    path('annonces/', views.annonces, name='gestion_annonces'),
    path('annonces/<int:pk>/', views.annonce_detail, name='gestion_annonce_detail'),
    path('annonces/<int:pk>/valider/', views.annonce_valider, name='gestion_annonce_valider'),
    path('annonces/<int:pk>/rejeter/', views.annonce_rejeter, name='gestion_annonce_rejeter'),

    # Gestionnaire dashboard
    path('tableau-de-bord/', views.gestionnaire_dashboard, name='gestion_gestionnaire_dashboard'),

    # Demandes partenaires (formulaire public)
    path('demandes-partenaires/', views.demandes_partenaires, name='gestion_demandes_partenaires'),
    path('demandes-partenaires/<int:pk>/valider/', views.demande_partenaire_valider, name='gestion_demande_valider'),
    path('demandes-partenaires/<int:pk>/refuser/', views.demande_partenaire_refuser, name='gestion_demande_refuser'),

    # Profil
    path('profil/', views.profil, name='gestion_profil'),
]
