# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.functional import cached_property
from django.utils.text import slugify

from multisync.ldap_synchronizers import LdapUserSynchronizer, LdapGroupSynchronizer, LdapUserGroupsSynchronizer
from multisync.models import LdapUser, LdapGroup, GitlabUser, GitlabGroup, GitlabMembers
from multisync.nrpe import NrpeCheck
from multisync.synchronizer import is_admin

__author__ = 'Matthieu Gallet'


class GitlabUserSynchronizer(LdapUserSynchronizer):
    user_cls = GitlabUser

    def get_copy_elements(self):
        query = self.user_cls.objects.all()
        if settings.DATABASE_USER_FILTER_KWARGS:
            query = query.filter(**settings.DATABASE_USER_FILTER_KWARGS)
        if settings.DATABASE_USER_EXCLUDE_KWARGS:
            query = query.exclude(**settings.DATABASE_USER_EXCLUDE_KWARGS)
        return query

    def prepare_delete_copy_element(self, copy_element):
        assert isinstance(copy_element, self.user_cls)
        if copy_element.state != 'active':
            return None
        if copy_element.admin:
            self.error_ids.append(copy_element.username)
        self.deleted_ids.append(copy_element.username)
        return copy_element.pk

    def get_copy_to_id(self, copy_element):
        assert isinstance(copy_element, self.user_cls)
        return copy_element.username

    def delete_copy_elements(self, prepared_copy_elements):
        self.user_cls.objects.filter(pk__in=prepared_copy_elements).update(state='blocked')

    def prepare_new_copy_element(self, ref_element):
        assert isinstance(ref_element, LdapUser)
        copy_element = self.user_cls(username=ref_element.name)
        self.sync_element(copy_element, ref_element)
        self.created_ids.append(ref_element.name)
        return copy_element

    def sync_element(self, copy_element, ref_element):
        if copy_element.admin and not is_admin(copy_element.username):
            self.error_ids.append(copy_element.username)
        must_save = copy_element.admin != is_admin(copy_element.username)
        copy_element.admin = is_admin(copy_element.username)
        must_save |= copy_element.email != ref_element.mail
        copy_element.email = ref_element.mail
        must_save |= copy_element.state != 'active'
        copy_element.state = 'active'
        expected_name = ref_element.display_name if ref_element.display_name.strip() else ref_element.name
        if is_admin(copy_element.username):
            expected_name += ' [Admin]'
        must_save |= copy_element.name != expected_name
        copy_element.name = expected_name
        return must_save

    def update_copy_element(self, copy_element, ref_element):
        assert isinstance(copy_element, self.user_cls)
        assert isinstance(ref_element, LdapUser)
        if self.sync_element(copy_element, ref_element):
            copy_element.save()
            self.modified_ids.append(copy_element.username)

    def create_copy_elements(self, prepared_copy_elements):
        self.user_cls.objects.bulk_create(prepared_copy_elements)


class GitlabGroupSynchronizer(LdapGroupSynchronizer):
    group_cls = GitlabGroup

    def get_copy_elements(self):
        query = self.group_cls.objects.all()
        if settings.DATABASE_GROUP_FILTER_KWARGS:
            query = query.filter(**settings.DATABASE_GROUP_FILTER_KWARGS)
        if settings.DATABASE_GROUP_EXCLUDE_KWARGS:
            query = query.exclude(**settings.DATABASE_GROUP_EXCLUDE_KWARGS)
        return query

    @cached_property
    def usernames(self):
        return {x.username: x.id for x in GitlabUserSynchronizer.user_cls.objects.all()}

    def prepare_delete_copy_element(self, copy_element):
        assert isinstance(copy_element, self.group_cls)
        if copy_element.name in self.usernames:
            return None
        self.deleted_ids.append(copy_element.name)
        return copy_element.pk

    def get_copy_to_id(self, copy_element):
        assert isinstance(copy_element, self.group_cls)
        return copy_element.name

    def delete_copy_elements(self, prepared_copy_elements):
        prepared_copy_elements = filter(lambda x: x, prepared_copy_elements)
        self.group_cls.objects.filter(pk__in=prepared_copy_elements).delete()

    def finalize_element(self, copy_element):
        must_save = False
        if copy_element.name in self.usernames:
            must_save |= (copy_element.owner_id != self.usernames[copy_element.name])
            copy_element.owner_id = self.usernames[copy_element.name]
            must_save |= (copy_element.type is not None)
            copy_element.type = None
        else:
            must_save |= (copy_element.owner_id is not None)
            copy_element.owner_id = None
            must_save |= (copy_element.type != 'Group')
            copy_element.type = 'Group'
        return must_save

    def prepare_new_copy_element(self, ref_element):
        assert isinstance(ref_element, LdapGroup)
        copy_element = self.group_cls(name=ref_element.name, path=slugify(ref_element.name),
                                      visibility_level=20)
        self.finalize_element(copy_element)
        self.created_ids.append(copy_element.name)
        return copy_element

    def update_copy_element(self, copy_element, ref_element):
        if self.finalize_element(copy_element):
            copy_element.save()
            self.modified_ids.append(copy_element.name)

    def create_copy_elements(self, prepared_copy_elements):
        self.group_cls.objects.bulk_create(prepared_copy_elements)


class GitlabUserGroupsSynchronizer(LdapUserGroupsSynchronizer):
    cls = GitlabMembers

    def __init__(self):
        super(GitlabUserGroupsSynchronizer, self).__init__()

        user_synchronizer = GitlabUserSynchronizer()
        group_synchronizer = GitlabGroupSynchronizer()

        self.user_pks = {x[0] for x in user_synchronizer.get_copy_elements().values_list('pk')}
        self.group_pks = {x[0] for x in group_synchronizer.get_copy_elements().values_list('pk')}
        self.group_id_to_name = {x.pk: x.name for x in GitlabGroup.objects.filter(pk__in=self.group_pks)}
        self.group_name_to_id = {x.name: x.pk for x in GitlabGroup.objects.filter(pk__in=self.group_pks)}
        self.user_id_to_name = {x.pk: x.username for x in GitlabUser.objects.filter(pk__in=self.user_pks)}
        self.user_name_to_id = {x.username: x.pk for x in GitlabUser.objects.filter(pk__in=self.user_pks)}

    def create_copy_elements(self, prepared_copy_elements):
        prepared_copy_elements = filter(lambda x: x, prepared_copy_elements)
        self.cls.objects.bulk_create(prepared_copy_elements)

    def get_copy_elements(self):
        return self.cls.objects.filter(source_type='Namespace', user_id__in=self.user_pks, source_id__in=self.group_pks,
                                       type='GroupMember')

    def get_copy_to_id(self, copy_element):
        return self.group_id_to_name[copy_element.source_id], self.user_id_to_name[copy_element.user_id]

    def prepare_new_copy_element(self, ref_element):
        group_name, user_name = ref_element
        if group_name in self.user_name_to_id:  # do not add users to user namespaces
            return None
        self.created_ids.setdefault(group_name, []).append(user_name)
        return self.cls(user_id=self.user_name_to_id[user_name],
                        source_id=self.group_name_to_id[group_name], source_type='Namespace', type='GroupMember',
                        notification_level=3, access_level=10)

    def prepare_delete_copy_element(self, copy_element):
        group_name = self.group_id_to_name[copy_element.source_id]
        user_name = self.user_id_to_name[copy_element.user_id]
        self.deleted_ids.setdefault(group_name, []).append(user_name)
        return copy_element.id

    def delete_copy_elements(self, prepared_copy_elements):
        self.cls.objects.filter(id__in=prepared_copy_elements).delete()

    def update_copy_element(self, copy_element, ref_element):
        pass


class GitlabSynchronizer(NrpeCheck):
    synchronizer_user_cls = GitlabUserSynchronizer
    synchronizer_group_cls = GitlabGroupSynchronizer
    synchronizer_usergroup_cls = GitlabUserGroupsSynchronizer
