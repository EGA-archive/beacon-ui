from django.urls import path
from django.views.generic import TemplateView

from .views import BeaconQueryView, BeaconAccessLevelsView, BeaconHistoryView
from .auth import BeaconLoginView, BeaconLogoutView

urlpatterns = [
    path('', BeaconQueryView.as_view(), name='query'),
    path('history/<int:index>', BeaconHistoryView.as_view(), name='history'),
    path('access-levels', BeaconAccessLevelsView.as_view(), name='levels'),
    path('login', BeaconLoginView.as_view(), name='login'),
    path('privacy', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('logout', BeaconLogoutView.as_view(), name='logout'),
] # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
