# A local settings override
#
# This is a sample settings file that will allow you to import everything
# from the base config and override any of them as necesssary.
#
# You need to set the `DJANGO_SETTINGS_MODULE` environment variable to
# use your own file instead of the base settings file like:
#
#    export DJANGO_SETTINGS_MODULE='werewolf.settings.my_local_settings'

from .base import *  # NOQA

DATABASES['default']['PASSWORD'] = 'DreydisdijrajQuaygcicapVoshbenig'
