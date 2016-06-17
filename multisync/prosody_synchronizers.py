# -*- coding: utf-8 -*-
import os
try:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from ConfigParser import ConfigParser
except ImportError:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from configparser import ConfigParser

from django.conf import settings

from multisync.ldap_synchronizers import LdapUserSynchronizer, LdapGroupSynchronizer
from multisync.nrpe import NrpeCheck

__author__ = 'Matthieu Gallet'


class ProsodySynchronizer(NrpeCheck):

    def synchronize(self):
        user_synchronizer = LdapUserSynchronizer()
        group_synchronizer = LdapGroupSynchronizer()
        users = {x.name: x.display_name for x in user_synchronizer.get_ref_elements()}
        parser = ConfigParser()
        for group in group_synchronizer.get_ref_elements():
            group_name = group.name.encode('utf-8')
            parser.add_section(group_name)
            for username in group.members:
                username = username.encode('utf-8')
                parser.set(group_name, '%s@%s' % (username, settings.PROSODY_DOMAIN),
                           users.get(username).strip() or username)
        with open(settings.PROSODY_GROUP_FILE + '.tmp', 'w') as fd:
            parser.write(fd)
        os.rename(settings.PROSODY_GROUP_FILE + '.tmp', settings.PROSODY_GROUP_FILE)
        return 0, ''
