# -*- coding: utf-8 -*-
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
        return LdapUser.objects.all()

    def get_ref_to_id(self, ref_element):
        assert isinstance(ref_element, LdapUser)
        return ref_element.name


# noinspection PyAbstractClass
class LdapGroupSynchronizer(Synchronizer):
    def __init__(self):
        self.deleted_ids = []
        self.created_ids = []

    def get_ref_elements(self):
        return LdapGroup.objects.all()

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
        for group in LdapGroup.objects.all():
            for username in group.members:
                yield (group.name, username)
