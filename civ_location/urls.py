from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('public.urls')),
    path('gestion/', include('gestion.urls')),
    path('partenaire/', include('partenaire.urls')),
    # Sert les fichiers media en production (DEBUG=False)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
