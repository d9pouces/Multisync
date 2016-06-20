# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ldapdb.models
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.core import validators
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from ldapdb.models.fields import CharField, IntegerField, ListField, ImageField as ImageField_


__author__ = 'flanker'
name_pattern = r'[a-zA-Z][\w_\-]{0,199}'
name_validators = [RegexValidator('^%s$' % name_pattern)]


def force_bytestrings(unicode_list):
    """
     >>> force_bytestrings(['test']) == [b'test']
     True
    """
    return [x.encode('utf-8') for x in unicode_list]


def force_bytestring(x):
    return x.encode('utf-8')


# noinspection PyClassHasNoInit
class ImageField(ImageField_):
    def get_internal_type(self):
        return 'CharField'


class BaseLdapModel(ldapdb.models.Model):
    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.name)

    class Meta(object):
        abstract = True


class LdapGroup(BaseLdapModel):
    base_dn = '%s,%s' % (settings.LDAP_GROUP_OU, settings.LDAP_BASE_DN)
    object_classes = force_bytestrings(['posixGroup', 'sambaGroupMapping'])
    # posixGroup attributes
    name = CharField(db_column=force_bytestring('cn'), max_length=200, primary_key=True,
                     validators=list(name_validators))
    gid = IntegerField(db_column=force_bytestring('gidNumber'), unique=True)
    members = ListField(db_column=force_bytestring('memberUid'))
    description = CharField(db_column=force_bytestring('description'), max_length=500, blank=True, default='')
    group_type = IntegerField(db_column=force_bytestring('sambaGroupType'), default=None)
    samba_sid = CharField(db_column=force_bytestring('sambaSID'), unique=True, default='')


class LdapUser(BaseLdapModel):
    base_dn = '%s,%s' % (settings.LDAP_USER_OU, settings.LDAP_BASE_DN)
    object_classes = force_bytestrings(['posixAccount', 'shadowAccount', 'inetOrgPerson', 'sambaSamAccount', 'person',
                                        'AsteriskSIPUser'])
    name = CharField(db_column=force_bytestring('uid'), max_length=200, primary_key=True,
                     validators=list(name_validators))
    display_name = CharField(db_column=force_bytestring('displayName'), max_length=200)
    uid_number = IntegerField(db_column=force_bytestring('uidNumber'), default=None, unique=True)
    gid_number = IntegerField(db_column=force_bytestring('gidNumber'), default=None)
    login_shell = CharField(db_column=force_bytestring('loginShell'), default='/bin/bash')
    description = CharField(db_column=force_bytestring('description'), default='Description')
    jpeg_photo = ImageField(db_column=force_bytestring('jpegPhoto'), max_length=10000000)
    phone = CharField(db_column=force_bytestring('telephoneNumber'), default=None)
    samba_acct_flags = CharField(db_column=force_bytestring('sambaAcctFlags'), default='[UX         ]')
    user_smime_certificate = CharField(db_column=force_bytestring('userSMIMECertificate'), default=None)
    user_certificate = CharField(db_column=force_bytestring('userCertificate'), default=None)
    # forced values
    samba_sid = CharField(db_column=force_bytestring('sambaSID'), default=None)
    primary_group_samba_sid = CharField(db_column=force_bytestring('sambaPrimaryGroupSID'), default=None)
    home_directory = CharField(db_column=force_bytestring('homeDirectory'), default=None)
    mail = CharField(db_column=force_bytestring('mail'), default=None)
    samba_domain_name = CharField(db_column=force_bytestring('sambaDomainName'), default=None)
    gecos = CharField(db_column=force_bytestring('gecos'), max_length=200, default=None)
    cn = CharField(db_column=force_bytestring('cn'), max_length=200, default=None, validators=list(name_validators))
    sn = CharField(db_column=force_bytestring('sn'), max_length=200, default=None, validators=list(name_validators))
    # password values
    user_password = CharField(db_column=force_bytestring('userPassword'), default=None)
    # samba_nt_password = CharField(db_column=force_bytestring('sambaNTPassword'), default=None)
    ast_account_caller_id = CharField(db_column=force_bytestring('AstAccountCallerID'), default=None)
    ast_account_context = CharField(db_column=force_bytestring('AstAccountContext'), default='LocalSets')
    ast_account_DTMF_mode = CharField(db_column=force_bytestring('AstAccountDTMFMode'), default='rfc2833')
    ast_account_mailbox = CharField(db_column=force_bytestring('AstAccountMailbox'), default=None)
    ast_account_NAT = CharField(db_column=force_bytestring('AstAccountNAT'), default='yes')
    ast_account_qualify = CharField(db_column=force_bytestring('AstAccountQualify'), default='yes')
    ast_account_type = CharField(db_column=force_bytestring('AstAccountType'), default='friend')
    ast_account_disallowed_codec = CharField(db_column=force_bytestring('AstAccountDisallowedCodec'), default='all')
    ast_account_allowed_codec = CharField(db_column=force_bytestring('AstAccountAllowedCodec'), default='ulaw')
    ast_account_music_on_hold = CharField(db_column=force_bytestring('AstAccountMusicOnHold'), default='default')


class Djangouser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField('username', max_length=250, unique=True,
                                help_text='Required. Letters, digits and "/"/@/./+/-/_ only.',
                                validators=[validators.RegexValidator(r'^[/\w.@+_\-]+$', 'Enter a valid username. ',
                                                                      'invalid'), ])
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    email = models.EmailField('email address', blank=True)
    is_staff = models.BooleanField('staff status', default=False,
                                   help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField('active', default=True,
                                    help_text=('Designates whether this user should be treated as '
                                               'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    objects = UserManager()

    class Meta(object):
        managed = False
        db_table = 'penatesserver_djangouser'

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name
