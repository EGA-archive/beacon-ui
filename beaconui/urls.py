from django.urls import path
from django.views.generic import TemplateView

from .views import EGABeaconInfoView, EGABeaconResultsView
from .aai import EGABeaconLoginView, EGABeaconLogoutView

urlpatterns = [
    path('', EGABeaconInfoView.as_view(), name='info'),
    path('query', EGABeaconResultsView.as_view(), name='query'),
    path('login', EGABeaconLoginView.as_view(), name='login'),
    path('privacy', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('logout', EGABeaconLogoutView.as_view(), name='logout'),
] # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
