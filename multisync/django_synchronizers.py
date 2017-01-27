# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from multisync.ldap_synchronizers import LdapUserSynchronizer, LdapGroupSynchronizer, LdapUserGroupsSynchronizer
from multisync.models import LdapUser, LdapGroup
from multisync.nrpe import NrpeCheck
from multisync.synchronizer import is_admin, guess_name_components

__author__ = 'Matthieu Gallet'


class DjangoUserSynchronizer(LdapUserSynchronizer):
    user_cls = get_user_model()

    def get_copy_elements(self):
        query = self.user_cls.objects.all()
        if settings.DATABASE_USER_FILTER_KWARGS:
            query = query.filter(**settings.DATABASE_USER_FILTER_KWARGS)
        if settings.DATABASE_USER_EXCLUDE_KWARGS:
            query = query.exclude(**settings.DATABASE_USER_EXCLUDE_KWARGS)
        return query

    def prepare_delete_copy_element(self, copy_element):
        assert isinstance(copy_element, self.user_cls)
        if copy_element.is_superuser:
            self.error_ids.append(copy_element.username)
        self.deleted_ids.append(copy_element.username)
        return copy_element.pk

    def get_copy_to_id(self, copy_element):
        assert isinstance(copy_element, self.user_cls)
        return copy_element.username

    def delete_copy_elements(self, prepared_copy_elements):
        self.user_cls.objects.filter(pk__in=prepared_copy_elements).delete()

    def prepare_new_copy_element(self, ref_element):
        assert isinstance(ref_element, LdapUser)
        copy_element = self.user_cls(username=ref_element.name)
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
        assert isinstance(copy_element, self.user_cls)
        assert isinstance(ref_element, LdapUser)
        save = self.sync_element(copy_element, ref_element)
        if save:
            copy_element.save()
            self.modified_ids.append(copy_element.username)

    def create_copy_elements(self, prepared_copy_elements):
        self.user_cls.objects.bulk_create(prepared_copy_elements)


class DjangoGroupSynchronizer(LdapGroupSynchronizer):
    group_cls = Group
    
    def get_copy_elements(self):
        query = self.group_cls.objects.all()
        if settings.DATABASE_GROUP_FILTER_KWARGS:
            query = query.filter(**settings.DATABASE_GROUP_FILTER_KWARGS)
        if settings.DATABASE_GROUP_EXCLUDE_KWARGS:
            query = query.exclude(**settings.DATABASE_GROUP_EXCLUDE_KWARGS)
        return query

    def prepare_delete_copy_element(self, copy_element):
        assert isinstance(copy_element, self.group_cls)
        self.deleted_ids.append(copy_element.name)
        return copy_element.pk

    def get_copy_to_id(self, copy_element):
        assert isinstance(copy_element, self.group_cls)
        return copy_element.name

    def delete_copy_elements(self, prepared_copy_elements):
        self.group_cls.objects.filter(pk__in=prepared_copy_elements).delete()

    def prepare_new_copy_element(self, ref_element):
        assert isinstance(ref_element, LdapGroup)
        copy_element = self.group_cls(name=ref_element.name)
        self.created_ids.append(copy_element.name)
        return copy_element

    def update_copy_element(self, copy_element, ref_element):
        pass

    def create_copy_elements(self, prepared_copy_elements):
        self.group_cls.objects.bulk_create(prepared_copy_elements)


class DjangoUserGroupsSynchronizer(LdapUserGroupsSynchronizer):
    # noinspection PyUnresolvedReferences
    cls = get_user_model().groups.through
    user_synchronizer_cls = DjangoUserSynchronizer
    group_synchronizer_cls = DjangoGroupSynchronizer

    def __init__(self):
        super(DjangoUserGroupsSynchronizer, self).__init__()
        # noinspection PyProtectedMember
        self.user_prefix = self.user_synchronizer_cls.user_cls._meta.model_name
        # noinspection PyProtectedMember
        self.group_prefix = self.group_synchronizer_cls.group_cls._meta.model_name

        user_synchronizer = self.user_synchronizer_cls()
        group_synchronizer = self.group_synchronizer_cls()
        group_cls = self.group_synchronizer_cls.group_cls
        user_cls = self.user_synchronizer_cls.user_cls
        self.user_pks = {x[0] for x in user_synchronizer.get_copy_elements().values_list('pk')}
        self.group_pks = {x[0] for x in group_synchronizer.get_copy_elements().values_list('pk')}
        self.group_id_to_name = {x.pk: x.name for x in group_cls.objects.filter(pk__in=self.group_pks)}
        self.group_name_to_id = {x.name: x.pk for x in group_cls.objects.filter(pk__in=self.group_pks)}
        self.user_id_to_name = {x.pk: x.username for x in user_cls.objects.filter(pk__in=self.user_pks)}
        self.user_name_to_id = {x.username: x.pk for x in user_cls.objects.filter(pk__in=self.user_pks)}

    def create_copy_elements(self, prepared_copy_elements):
        self.cls.objects.bulk_create(prepared_copy_elements)

    def get_copy_elements(self):
        kwargs = {'%s__pk__in' % self.user_prefix: self.user_pks, '%s__pk__in' % self.group_prefix: self.group_pks}
        return self.cls.objects.filter(**kwargs)

    def get_copy_to_id(self, copy_element):
        user_id = getattr(copy_element, '%s_id' % self.user_prefix)
        group_id = getattr(copy_element, '%s_id' % self.group_prefix)
        return self.group_id_to_name[group_id], self.user_id_to_name[user_id]

    def prepare_new_copy_element(self, ref_element):
        group_name, user_name = ref_element
        self.created_ids.setdefault(group_name, []).append(user_name)
        kwargs = {'%s_id' % self.user_prefix: self.user_name_to_id[user_name],
                  '%s_id' % self.group_prefix: self.group_name_to_id[group_name]}
        return self.cls(**kwargs)

    def prepare_delete_copy_element(self, copy_element):
        user_id = getattr(copy_element, '%s_id' % self.user_prefix)
        group_id = getattr(copy_element, '%s_id' % self.group_prefix)
        group_name = self.group_id_to_name[group_id]
        user_name = self.user_id_to_name[user_id]
        self.deleted_ids.setdefault(group_name, []).append(user_name)
        kwargs = {'%s_id' % self.user_prefix: user_id,  '%s_id' % self.group_prefix: group_id}
        return self.cls(**kwargs)

    def delete_copy_elements(self, prepared_copy_elements):
        pass

    def update_copy_element(self, copy_element, ref_element):
        pass


class DjangoSynchronizer(NrpeCheck):
    synchronizer_user_cls = DjangoUserSynchronizer
    synchronizer_group_cls = DjangoGroupSynchronizer
    synchronizer_usergroup_cls = DjangoUserGroupsSynchronizer
