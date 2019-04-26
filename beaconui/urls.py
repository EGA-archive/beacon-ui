from django.urls import path
from django.views.generic import TemplateView

from .views import BeaconView, BeaconAccessLevelsView
from .auth import BeaconLoginView, BeaconLogoutView

urlpatterns = [
    path('', BeaconView.as_view(), name='beacon'),
    path('access-levels', BeaconAccessLevelsView.as_view(), name='levels'),
    path('login', BeaconLoginView.as_view(), name='login'),
    path('privacy', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('logout', BeaconLogoutView.as_view(), name='logout'),
] # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
