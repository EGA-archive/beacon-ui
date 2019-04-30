from django.urls import path
from django.views.generic import TemplateView

from .views import BeaconQueryView, BeaconGenomicRegionView, BeaconGenomicSNPView, BeaconAccessLevelsView, BeaconHistoryView
from .auth import BeaconLoginView, BeaconLogoutView

urlpatterns = [
    path('', BeaconQueryView.as_view(), name='query'),
    path('genomic-region', BeaconGenomicRegionView.as_view(), name='genomic-region'),
    path('genomic-snp', BeaconGenomicSNPView.as_view(), name='genomic-snp'),
    path('history/<int:index>', BeaconHistoryView.as_view(), name='history'),
    path('access-levels', BeaconAccessLevelsView.as_view(), name='levels'),
    path('login', BeaconLoginView.as_view(), name='login'),
    path('privacy', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('logout', BeaconLogoutView.as_view(), name='logout'),
] # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
