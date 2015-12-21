# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'Matthieu Gallet'

########################################################################################################################

FLOOR_INSTALLED_APPS = ['multisync', ]
FLOOR_URL_CONF = 'multisync.root_urls.urls'
FLOOR_PROJECT_NAME = 'MultiSync'

LDAP_BASE_DN = 'dc=test,dc=example,dc=org'
LDAP_NAME = 'ldap://192.168.56.101/'
LDAP_USER = 'cn=admin,dc=test,dc=example,dc=org'
LDAP_PASSWORD = 'toto'

SYNCHRONIZER = 'multisync.django_synchronizers.DjangoSynchronizer'

DATABASES = {
    'default': {
        'ENGINE': '{DATABASE_ENGINE}',
        'NAME': '{DATABASE_NAME}',
        'USER': '{DATABASE_USER}',
        'PASSWORD': '{DATABASE_PASSWORD}',
        'HOST': '{DATABASE_HOST}',
        'PORT': '{DATABASE_PORT}',
    },
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': '{LDAP_NAME}',
        'USER': '{LDAP_USER}',
        'PASSWORD': '{LDAP_PASSWORD}',
    },
}

DATABASE_ROUTERS = ['ldapdb.router.Router', ]

PROSODY_GROUP_FILE = '{LOCAL_PATH}/groups.ini'
PROSODY_DOMAIN = 'im.example.org'