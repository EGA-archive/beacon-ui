from django.apps import AppConfig

class EGABeaconConfig(AppConfig):
    name = 'beaconui'
    verbose_name = "EGA Beacon Frontend"


default_app_config = 'beaconui.EGABeaconConfig'
