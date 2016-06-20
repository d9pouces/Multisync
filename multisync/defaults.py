# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'Matthieu Gallet'

########################################################################################################################

FLOOR_INSTALLED_APPS = ['multisync', ]
FLOOR_URL_CONF = 'multisync.root_urls.urls'
FLOOR_PROJECT_NAME = 'MultiSync'

LDAP_BASE_DN = 'dc=test,dc=example,dc=org'
LDAP_BASE_DN_HELP = 'base dn for searching users and groups, like dc=test,dc=example,dc=org.'
LDAP_GROUP_OU = 'ou=Groups'
LDAP_GROUP_OU_HELP = 'subtree containing groups, like ou=Groups'
LDAP_USER_OU = 'ou=Users'
LDAP_USER_OU_HELP = 'subtree containing users, like ou=Users'
LDAP_NAME = 'ldap://192.168.56.101/'
LDAP_NAME_HELP = 'LDAP url, like ldap://127.0.0.1/ or ldapi:///'
LDAP_USER = 'cn=admin,dc=test,dc=example,dc=org'
LDAP_USER_HELP = 'LDAP user name to bind with'
LDAP_PASSWORD = 'toto'
LDAP_PASSWORD_HELP = 'LDAP password to bind with'
LDAP_GROUP_FILTER_KWARGS = {}
LDAP_GROUP_EXCLUDE_KWARGS = {}
LDAP_USER_FILTER_KWARGS = {}
LDAP_USER_EXCLUDE_KWARGS = {}

SYNCHRONIZER = 'multisync.django_synchronizers.DjangoSynchronizer'
AUTH_USER_MODEL = 'auth.User'
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
DATABASE_GROUP_FILTER_KWARGS = {}
DATABASE_GROUP_EXCLUDE_KWARGS = {}
DATABASE_USER_FILTER_KWARGS = {}
DATABASE_USER_EXCLUDE_KWARGS = {}


PROSODY_GROUP_FILE = '{LOCAL_PATH}/groups.ini'
PROSODY_GROUP_FILE_HELP = 'path of the generated Prosody config file. ' \
                          'See `https://prosody.im/doc/modules/mod_groups#example` for more info.'
PROSODY_DOMAIN = 'im.example.org'
PROSODY_DOMAIN_HELP = 'Domain to append to the Prosody\'s usernames'
