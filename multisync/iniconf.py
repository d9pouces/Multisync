# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from djangofloor.iniconf import OptionParser

__author__ = 'Matthieu Gallet'

INI_MAPPING = [

    OptionParser('DATABASE_ENGINE', 'database.engine'),
    OptionParser('DATABASE_NAME', 'database.name'),
    OptionParser('DATABASE_USER', 'database.user'),
    OptionParser('DATABASE_PASSWORD', 'database.password'),
    OptionParser('DATABASE_HOST', 'database.host'),
    OptionParser('DATABASE_PORT', 'database.port'),

    OptionParser('LDAP_BASE_DN', 'ldap.base_dn'),
    OptionParser('LDAP_NAME', 'ldap.name'),
    OptionParser('LDAP_USER', 'ldap.user'),
    OptionParser('LDAP_PASSWORD', 'ldap.password'),
    OptionParser('LDAP_GROUP_OU', 'ldap.group_ou'),
    OptionParser('LDAP_USER_OU', 'ldap.user_ou'),

    OptionParser('SYNCHRONIZER', 'multisync.synchronizer'),
    OptionParser('PROSODY_GROUP_FILE', 'prosody.group_file'),
    OptionParser('PROSODY_DOMAIN', 'prosody.domain'),
    OptionParser('ADMIN_EMAIL', 'global.admin_email'),
    OptionParser('TIME_ZONE', 'global.time_zone'),
    OptionParser('LANGUAGE_CODE', 'global.language_code'),
    OptionParser('FLOOR_DEFAULT_GROUP_NAME', 'global.default_group'),

    ]
