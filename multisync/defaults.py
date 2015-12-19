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
