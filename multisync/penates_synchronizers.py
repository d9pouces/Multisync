# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from multisync.django_synchronizers import DjangoGroupSynchronizer

from multisync.ldap_synchronizers import LdapUserSynchronizer, LdapUserGroupsSynchronizer
from multisync.models import LdapUser, PenatesserverDjangouser, PenatesserverDjangouserGroups
from multisync.nrpe import NrpeCheck
from multisync.synchronizer import is_admin, guess_name_components


__author__ = 'Matthieu Gallet'


class PenatesUserSynchronizer(LdapUserSynchronizer):

    def get_copy_elements(self):
        return PenatesserverDjangouser.objects.all()

    def prepare_delete_copy_element(self, copy_element):
        assert isinstance(copy_element, PenatesserverDjangouser)
        if copy_element.is_superuser:
            self.error_ids.append(copy_element.username)
        self.deleted_ids.append(copy_element.username)
        return copy_element.pk

    def get_copy_to_id(self, copy_element):
        assert isinstance(copy_element, PenatesserverDjangouser)
        return copy_element.username

    def delete_copy_elements(self, prepared_copy_elements):
        PenatesserverDjangouser.objects.filter(pk__in=prepared_copy_elements).delete()

    def prepare_new_copy_element(self, ref_element):
        assert isinstance(ref_element, LdapUser)
        copy_element = PenatesserverDjangouser(username=ref_element.name)
        self.sync_element(copy_element, ref_element)
        self.created_ids.append(ref_element.name)
        return copy_element

    def sync_element(self, copy_element, ref_element):
        if copy_element.is_superuser and not is_admin(copy_element.username):
            self.error_ids.append(copy_element.username)
        must_save = copy_element.is_superuser != is_admin(copy_element.username)
        copy_element.is_superuser = is_admin(copy_element.username)
        must_save |= copy_element.is_superuser != copy_element.is_staff
        copy_element.is_staff = copy_element.is_superuser
        must_save |= copy_element.email != ref_element.mail
        copy_element.email = ref_element.mail
        first_name, last_name = guess_name_components(ref_element.display_name)
        if copy_element.first_name != first_name:
            copy_element.first_name = first_name
            must_save = True
        if copy_element.last_name != last_name:
            copy_element.last_name = last_name
            must_save = True
        return must_save

    def update_copy_element(self, copy_element, ref_element):
        assert isinstance(copy_element, PenatesserverDjangouser)
        assert isinstance(ref_element, LdapUser)
        save = self.sync_element(copy_element, ref_element)
        if save:
            copy_element.save()
            self.modified_ids.append(copy_element.username)

    def create_copy_elements(self, prepared_copy_elements):
        PenatesserverDjangouser.objects.bulk_create(prepared_copy_elements)


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
        return PenatesserverDjangouserGroups(user_id=self.user_name_to_id[user_name],
                                             group_id=self.group_name_to_id[group_name])

    def prepare_delete_copy_element(self, copy_element):
        group_name = self.group_id_to_name[copy_element.group_id]
        user_name = self.user_id_to_name[copy_element.djangouser_id]
        self.deleted_ids.setdefault(group_name, []).append(user_name)
        PenatesserverDjangouserGroups.objects\
            .filter(user__id=copy_element.djangouser_id, group__id=copy_element.group_id).delete()

    def delete_copy_elements(self, prepared_copy_elements):
        pass

    def update_copy_element(self, copy_element, ref_element):
        pass


class PenatesSynchronizer(NrpeCheck):
    synchronizer_user_cls = PenatesUserSynchronizer
    synchronizer_group_cls = DjangoGroupSynchronizer
    synchronizer_usergroup_cls = PenatesUserGroupsSynchronizer
