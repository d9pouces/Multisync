# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import traceback

from django.core.management import BaseCommand


__author__ = 'Matthieu Gallet'


class NrpeCheck(BaseCommand):

    synchronizer_user_cls = None
    synchronizer_group_cls = None
    synchronizer_usergroup_cls = None

    def synchronize(self):
        output = ''
        exit_code = 0

        synchronizer = self.synchronizer_user_cls()
        synchronizer.synchronize()
        if synchronizer.error_ids:
            output += ('Users that should not be admin: %s\n' % ', '.join(synchronizer.error_ids))
            exit_code = max(exit_code, 2)
        if synchronizer.modified_ids:
            output += ('Modified users: %s\n' % ', '.join(synchronizer.modified_ids))
            exit_code = max(exit_code, 1)
        if synchronizer.deleted_ids:
            output += ('Deleted users: %s\n' % ', '.join(synchronizer.deleted_ids))
            exit_code = max(exit_code, 2)
        if synchronizer.created_ids:
            output += ('Created users: %s\n' % ', '.join(synchronizer.created_ids))
            exit_code = max(exit_code, 1)

        synchronizer = self.synchronizer_group_cls()
        synchronizer.synchronize()
        if synchronizer.created_ids:
            output += ('Created groups: %s\n' % ', '.join(synchronizer.created_ids))
            exit_code = max(exit_code, 1)
        if synchronizer.modified_ids:
            output += ('Modified groups: %s\n' % ', '.join(synchronizer.modified_ids))
            exit_code = max(exit_code, 1)
        if synchronizer.deleted_ids:
            output += ('Deleted groups: %s\n' % ', '.join(synchronizer.deleted_ids))
            exit_code = max(exit_code, 1)

        synchronizer = self.synchronizer_usergroup_cls()
        synchronizer.synchronize()
        if synchronizer.created_ids:
            for group_name, user_names in synchronizer.created_ids.items():
                output += ('Added to %s: %s\n' % (group_name, ', '.join(user_names)))
            exit_code = max(exit_code, 1)
        if synchronizer.deleted_ids:
            for group_name, user_names in synchronizer.deleted_ids.items():
                output += ('Removed from %s: %s\n' % (group_name, ', '.join(user_names)))
            exit_code = max(exit_code, 1)
        return exit_code, output

    def handle(self, *args, **options):
        try:
            exit_code, output = self.synchronize()
        except Exception as e:
            exit_code = 3
            output = '%s: %s\n' % (e.__class__.__name__, e)
            output += traceback.format_exc()

        if exit_code == 0:
            self.stdout.write('OK - all users and groups are valid\n')
        elif exit_code == 1:
            self.stdout.write('WARN - ')
        elif exit_code == 2:
            self.stdout.write('CRITICAL - ')
        elif exit_code == 3:
            self.stdout.write('UNKNOWN - Unable to synchronize\n')
        self.stdout.write(output.strip())
        return exit_code