from django.urls import path
from . import views

urlpatterns = [
    path('connexion/', views.connexion, name='partenaire_connexion'),
    path('deconnexion/', views.deconnexion, name='partenaire_deconnexion'),
    path('tableau-de-bord/', views.dashboard, name='partenaire_dashboard'),
    path('annonces/', views.annonces, name='partenaire_annonces'),
    path('annonces/ajouter/', views.annonce_ajouter, name='partenaire_annonce_ajouter'),
    path('annonces/<int:pk>/modifier/', views.annonce_modifier, name='partenaire_annonce_modifier'),
    path('annonces/<int:pk>/supprimer/', views.annonce_supprimer, name='partenaire_annonce_supprimer'),
    path('reservations/', views.reservations, name='partenaire_reservations'),
    path('profil/', views.profil, name='partenaire_profil'),
]
