from django.urls import path

from .views import EGABeaconInfoView, EGABeaconResultsView

urlpatterns = [
    path('', EGABeaconInfoView.as_view(), name='index'),
    path('query', EGABeaconResultsView.as_view(), name='index'),
    #path('<filename>', EGABeaconQueryView.as_view(), name='egafile'),
] # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
