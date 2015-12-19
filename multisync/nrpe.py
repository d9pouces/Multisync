# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management import BaseCommand
from multisync.ldap_synchronizers import LdapUserSynchronizer, LdapGroupSynchronizer, LdapUserGroupsSynchronizer


__author__ = 'Matthieu Gallet'


class NrpeCheck(BaseCommand):

    synchronizer_user_cls = None
    synchronizer_group_cls = None
    synchronizer_usergroup_cls = None

    def __init__(self):
        super(NrpeCheck, self).__init__()
        self.synchronizer_user = self.synchronizer_user_cls()
        self.synchronizer_group = self.synchronizer_group_cls()
        self.synchronizer_usergroup = self.synchronizer_usergroup_cls()

    def synchronize(self, exit_code):
        output = ''
        self.synchronizer_user.synchronize()
        if self.synchronizer_user.error_ids:
            output += ('Users that should not be admin: %s\n' % ', '.join(self.synchronizer_user.error_ids))
            exit_code = max(exit_code, 2)
        if self.synchronizer_user.modified_ids:
            output += ('Modified users: %s\n' % ', '.join(self.synchronizer_user.modified_ids))
            exit_code = max(exit_code, 1)
        if self.synchronizer_user.deleted_ids:
            output += ('Deleted users: %s\n' % ', '.join(self.synchronizer_user.deleted_ids))
            exit_code = max(exit_code, 2)
        if self.synchronizer_user.created_ids:
            output += ('Created users: %s\n' % ', '.join(self.synchronizer_user.created_ids))
            exit_code = max(exit_code, 1)
        self.synchronizer_group.synchronize()
        if self.synchronizer_group.created_ids:
            output += ('Created groups: %s\n' % ', '.join(self.synchronizer_group.created_ids))
            exit_code = max(exit_code, 1)
        if self.synchronizer_group.deleted_ids:
            output += ('Deleted groups: %s\n' % ', '.join(self.synchronizer_group.deleted_ids))
            exit_code = max(exit_code, 1)
        self.synchronizer_usergroup.synchronize()
        if self.synchronizer_group.created_ids:
            for group_name, user_names in self.synchronizer_group.created_ids.items():
                output += ('Added to %s: %s\n' % (group_name, ', '.join(user_names)))
            exit_code = max(exit_code, 1)
        if self.synchronizer_group.deleted_ids:
            for group_name, user_names in self.synchronizer_group.deleted_ids.items():
                output += ('Removed from %s: %s\n' % (group_name, ', '.join(user_names)))
            exit_code = max(exit_code, 1)
        return exit_code, output

    def handle(self, *args, **options):
        exit_code = 0
        assert isinstance(self.synchronizer_user, LdapUserSynchronizer)
        assert isinstance(self.synchronizer_group, LdapGroupSynchronizer)
        assert isinstance(self.synchronizer_usergroup, LdapUserGroupsSynchronizer)

        try:
            exit_code, output = self.synchronize(exit_code)
        except Exception as e:
            exit_code = 3
            output = '%s: %s' % (e.__class__.__name__, e)

        if exit_code == 0:
            self.stdout.write('OK - all users and groups are valid\n')
        elif exit_code == 1:
            self.stdout.write('WARN - ')
        elif exit_code == 2:
            self.stdout.write('CRITICAL - ')
        elif exit_code == 3:
            self.stdout.write('UNKNOWN - Unable to synchronize\n')
        self.stdout.write(output)
        return exit_code