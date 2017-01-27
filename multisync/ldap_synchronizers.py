# -*- coding: utf-8 -*-
from django.conf import settings

from multisync.models import LdapUser, LdapGroup
from multisync.synchronizer import Synchronizer

__author__ = 'Matthieu Gallet'


# noinspection PyAbstractClass
class LdapUserSynchronizer(Synchronizer):
    def __init__(self):
        self.error_ids = []
        self.modified_ids = []
        self.deleted_ids = []
        self.created_ids = []

    def get_ref_elements(self):
        query = LdapUser.objects.all()
        if settings.LDAP_USER_FILTER_KWARGS:
            query = query.filter(**settings.LDAP_USER_FILTER_KWARGS)
        if settings.LDAP_USER_EXCLUDE_KWARGS:
            query = query.exclude(**settings.LDAP_USER_EXCLUDE_KWARGS)
        return query

    def get_ref_to_id(self, ref_element):
        assert isinstance(ref_element, LdapUser)
        return ref_element.name


# noinspection PyAbstractClass
class LdapGroupSynchronizer(Synchronizer):
    def __init__(self):
        self.deleted_ids = []
        self.modified_ids = []
        self.created_ids = []

    def get_ref_elements(self):
        query = LdapGroup.objects.all()
        if settings.LDAP_GROUP_FILTER_KWARGS:
            query = query.filter(**settings.LDAP_GROUP_FILTER_KWARGS)
        if settings.LDAP_GROUP_EXCLUDE_KWARGS:
            query = query.exclude(**settings.LDAP_GROUP_EXCLUDE_KWARGS)
        return query

    def get_ref_to_id(self, ref_element):
        assert isinstance(ref_element, LdapGroup)
        return ref_element.name


# noinspection PyAbstractClass
class LdapUserGroupsSynchronizer(Synchronizer):

    def __init__(self):
        self.deleted_ids = {}
        self.created_ids = {}

    def get_ref_to_id(self, ref_element):
        return ref_element

    def get_ref_elements(self):
        query = LdapGroup.objects.all()
        if settings.LDAP_GROUP_FILTER_KWARGS:
            query = query.filter(**settings.LDAP_GROUP_FILTER_KWARGS)
        if settings.LDAP_GROUP_EXCLUDE_KWARGS:
            query = query.exclude(**settings.LDAP_GROUP_EXCLUDE_KWARGS)
        for group in query:
            for username in group.members:
                yield (group.name, username)
