# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group

from multisync.django_synchronizers import DjangoGroupSynchronizer, DjangoUserSynchronizer

from multisync.ldap_synchronizers import LdapUserGroupsSynchronizer
from multisync.models import PenatesserverDjangouser, PenatesserverDjangouserGroups
from multisync.nrpe import NrpeCheck


__author__ = 'Matthieu Gallet'


class PenatesUserSynchronizer(DjangoUserSynchronizer):
    user_cls = PenatesserverDjangouser


class PenatesUserGroupsSynchronizer(LdapUserGroupsSynchronizer):

    def __init__(self):
        super(PenatesUserGroupsSynchronizer, self).__init__()
        self.group_id_to_name = {x.pk: x.name for x in Group.objects.all()}
        self.group_name_to_id = {x.name: x.pk for x in Group.objects.all()}
        self.user_id_to_name = {x.pk: x.username for x in PenatesserverDjangouser.objects.all()}
        self.user_name_to_id = {x.username: x.pk for x in PenatesserverDjangouser.objects.all()}

    def create_copy_elements(self, prepared_copy_elements):
        PenatesserverDjangouserGroups.objects.bulk_create(prepared_copy_elements)

    def get_copy_elements(self):
        return PenatesserverDjangouserGroups.objects.all()

    def get_copy_to_id(self, copy_element):
        return self.group_id_to_name[copy_element.group_id], self.user_id_to_name[copy_element.djangouser_id]

    def prepare_new_copy_element(self, ref_element):
        group_name, user_name = ref_element
        self.created_ids.setdefault(group_name, []).append(user_name)
        return PenatesserverDjangouserGroups(djangouser_id=self.user_name_to_id[user_name],
                                             group_id=self.group_name_to_id[group_name])

    def prepare_delete_copy_element(self, copy_element):
        group_name = self.group_id_to_name[copy_element.group_id]
        user_name = self.user_id_to_name[copy_element.djangouser_id]
        self.deleted_ids.setdefault(group_name, []).append(user_name)
        PenatesserverDjangouserGroups.objects\
            .filter(djangouser__id=copy_element.djangouser_id, group_id=copy_element.group_id).delete()

    def delete_copy_elements(self, prepared_copy_elements):
        pass

    def update_copy_element(self, copy_element, ref_element):
        pass


class PenatesGroupSynchronizer(DjangoGroupSynchronizer):

    def delete_copy_elements(self, prepared_copy_elements):
        super(PenatesGroupSynchronizer, self).delete_copy_elements(prepared_copy_elements)
        PenatesserverDjangouserGroups.objects.filter(group_id__in=prepared_copy_elements).delete()


class PenatesSynchronizer(NrpeCheck):
    synchronizer_user_cls = PenatesUserSynchronizer
    synchronizer_group_cls = DjangoGroupSynchronizer
    synchronizer_usergroup_cls = PenatesUserGroupsSynchronizer
