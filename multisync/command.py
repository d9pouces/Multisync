# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import os
import sys
from django.utils.module_loading import import_string
from djangofloor.scripts import set_env

__author__ = 'Matthieu Gallet'


def main():
    parser = ArgumentParser()
    parser.add_argument('conf')
    options = parser.parse_args()

    ini_settings_path = options.conf
    os.environ['DJANGO_SETTINGS_MODULE'] = 'djangofloor.settings'
    os.environ['DJANGOFLOOR_INI_SETTINGS'] = os.path.abspath(ini_settings_path)
    os.environ['DJANGOFLOOR_PROJECT_DEFAULTS'] = 'multisync.defaults'
    os.environ['DJANGOFLOOR_PROJECT_NAME'] = 'multisync'

    set_env()
    import django
    django.setup()
    from django.conf import settings
    nrpe_check_cls = import_string(settings.SYNCHRONIZER)
    nrpe_check = nrpe_check_cls()
    exit_code = nrpe_check.handle()
    sys.exit(exit_code)
