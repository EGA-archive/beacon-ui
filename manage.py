#!/usr/bin/env python
import os
import sys
import logging
import logging.config
import yaml


if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beaconui.settings")
    from django.core.management import execute_from_command_line

    # Logging
    LOG_YML = os.getenv('LOG_YML', os.path.join(os.path.dirname(__file__),'logger.yaml'))
    if os.path.exists(LOG_YML):
        with open(LOG_YML, 'rt') as stream:
            #print('Using logger',LOG_YML)
            logging.config.dictConfig(yaml.load(stream))

    # Aaaaand...cue music!
    execute_from_command_line(sys.argv)

