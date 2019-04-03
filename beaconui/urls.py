from django.urls import path

from .views import EGABeaconInfoView#, EGABeaconQueryView

urlpatterns = [
    path('', EGABeaconInfoView.as_view(), name='index'),
    #path('<filename>', EGABeaconQueryView.as_view(), name='egafile'),
] # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
