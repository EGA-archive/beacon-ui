from django.urls import path
from django.views.generic import TemplateView

from .views import BeaconQueryView, BeaconSNPView, BeaconRegionView, BeaconAccessLevelsView
from .auth import BeaconLoginView, BeaconLogoutView

urlpatterns = [
    # Query endpoints
    path('', BeaconQueryView.as_view(), name='query'),
    path('snp', BeaconSNPView.as_view(), name='snp'),
    path('region', BeaconRegionView.as_view(), name='region'),
    # Access Levels
    path('access-levels', BeaconAccessLevelsView.as_view(), name='levels'),
    # Login endpoints
    path('login', BeaconLoginView.as_view(), name='login'),
    path('privacy', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('logout', BeaconLogoutView.as_view(), name='logout'),
]
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
