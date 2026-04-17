from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('vehicule/<int:pk>/', views.detail_vehicule, name='detail_vehicule'),
    path('reserver/<int:pk>/', views.reservation, name='reservation'),
    path('ma-reservation/', views.suivi_reservation, name='suivi_reservation'),
    path('devenir-partenaire/', views.devenir_partenaire, name='devenir_partenaire'),
]
