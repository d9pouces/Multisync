# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import os
import sys
from django.utils.module_loading import import_string
from djangofloor.scripts import set_env

__author__ = 'Matthieu Gallet'


def main():
    project_name = 'multisync'

    parser = ArgumentParser()
    parser.add_argument('conf')
    options = parser.parse_args()

    conf_name = options.conf
    prefix = sys.prefix
    if prefix == '/usr':
        prefix = ''
    ini_settings_path = os.path.abspath(os.path.join('.', '%s_configuration.ini' % project_name))
    if not os.path.isfile(ini_settings_path):
        ini_settings_path = '%s/etc/%s/%s.ini' % (prefix, project_name, conf_name)
    os.environ.setdefault("DJANGOFLOOR_INI_SETTINGS", os.path.abspath(ini_settings_path))
    set_env()

    from django.conf import settings
    nrpe_check_cls = import_string(settings.SYNCHRONIZER)
    nrpe_check = nrpe_check_cls()
    exit_code = nrpe_check.handle()
    sys.exit(exit_code)
