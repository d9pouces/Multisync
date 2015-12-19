# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User, Group
from django.test import TestCase
from multisync.django_synchronizers import DjangoUserSynchronizer, DjangoGroupSynchronizer, DjangoUserGroupsSynchronizer
from multisync.models import LdapUser, LdapGroup

__author__ = 'Matthieu Gallet'


class UserSynchronizer(DjangoUserSynchronizer):
    def get_ref_elements(self):
        yield LdapUser(display_name='Absent FROM DJANGO',
                       mail='absent.from-django@test.example.org',
                       name='afromdjango')
        yield LdapUser(display_name='Absent FROM DJANGO',
                       mail='afromdjango_admin@test.example.org',
                       name='afromdjango_admin')
        yield LdapUser(display_name='Present IN DJANGO',
                       mail='present.in-django@test.example.org',
                       name='presentindjango')
        yield LdapUser(display_name='NotAdmin IN DJANGO',
                       mail='notadmin.in-django@test.example.org',
                       name='notadminindjango')
        yield LdapUser(display_name='NotAdmin IN DJANGO',
                       mail='notadmin.in-django_admin@test.example.org',
                       name='notadminindjango_admin')
        yield LdapUser(display_name='Present IN DJANGO',
                       mail='presentindjango_admin@test.example.org',
                       name='presentindjango_admin')


class GroupSynchronizer(DjangoGroupSynchronizer):
    def get_ref_elements(self):
        yield LdapGroup(name='g_afromdjango')
        yield LdapGroup(name='g_emptydjango')
        yield LdapGroup(name='g_membersdjango', members=['presentindjango_admin', 'notadminindjango'])


class UserGroupSynchronizer(DjangoUserGroupsSynchronizer):
    def get_ref_elements(self):
        yield ('g_membersdjango', 'presentindjango_admin')
        yield ('g_membersdjango', 'notadminindjango')


class TestDjangoSynchronizer(TestCase):

    @classmethod
    def setUpClass(cls):
        TestCase.setUpClass()
        User(username='presentindjango', first_name='Present', last_name='IN DJANGO',
             email='present.in-django@test.example.org').save()
        User(username='notadminindjango', is_superuser=True, is_staff=True).save()
        User(username='notadminindjango_admin', is_superuser=False, is_staff=False).save()
        u2 = User(username='presentindjango_admin', is_superuser=True, is_staff=True)
        u2.save()
        User(username='notinldap').save()
        Group(name='presentindjango').save()
        g1 = Group(name='g_emptydjango')
        g1.save()
        g2 = Group(name='g_membersdjango')
        g2.save()
        u2.groups.add(g1)
        u2.groups.add(g2)

    def test_user(self):
        self.assertEqual(1, User.objects.filter(username='notinldap').count())
        self.assertEqual(1, User.objects.filter(username='notadminindjango').count())
        self.assertEqual(1, User.objects.filter(username='notadminindjango_admin').count())
        self.assertEqual(1, User.objects.filter(username='presentindjango_admin').count())
        self.assertEqual(0, User.objects.filter(username='afromdjango').count())
        self.assertEqual(0, User.objects.filter(username='afromdjango_admin').count())
        synchronizer = UserSynchronizer()
        synchronizer.synchronize()
        self.assertEqual(0, User.objects.filter(username='notinldap').count())
        self.assertEqual(0, User.objects.filter(username='notadminindjango', is_superuser=True).count())
        self.assertEqual(1, User.objects.filter(username='notadminindjango', is_superuser=False).count())
        self.assertEqual(1, User.objects.filter(username='presentindjango_admin', is_superuser=True).count())
        self.assertEqual(0, User.objects.filter(username='presentindjango_admin', is_superuser=False).count())
        self.assertEqual(0, User.objects.filter(username='notadminindjango_admin', is_superuser=False).count())
        self.assertEqual(1, User.objects.filter(username='notadminindjango_admin', is_superuser=True).count())
        self.assertEqual(1, User.objects.filter(username='afromdjango', is_superuser=False).count())
        self.assertEqual(1, User.objects.filter(username='afromdjango_admin', is_superuser=True).count())
        self.assertEqual(['afromdjango', 'afromdjango_admin'], synchronizer.created_ids)
        self.assertEqual(['notadminindjango', 'presentindjango_admin', 'notadminindjango_admin'],
                         synchronizer.modified_ids)
        self.assertEqual(['notadminindjango'], synchronizer.error_ids)
        self.assertEqual(['notinldap'], synchronizer.deleted_ids)

    def test_group(self):
        self.assertEqual(0, Group.objects.filter(name='g_afromdjango').count())
        self.assertEqual(1, Group.objects.filter(name='g_emptydjango').count())
        self.assertEqual(1, Group.objects.filter(name='g_membersdjango').count())
        self.assertEqual(1, Group.objects.filter(name='presentindjango').count())
        GroupSynchronizer().synchronize()
        self.assertEqual(1, Group.objects.filter(name='g_afromdjango').count())
        self.assertEqual(1, Group.objects.filter(name='g_emptydjango').count())
        self.assertEqual(1, Group.objects.filter(name='g_membersdjango').count())
        self.assertEqual(0, Group.objects.filter(name='presentindjango').count())

    def test_usergroup(self):
        # noinspection PyUnresolvedReferences
        self.assertEqual(2, User.groups.through.objects.all().count())
        UserGroupSynchronizer().synchronize()
        # noinspection PyUnresolvedReferences
        self.assertEqual(2, User.groups.through.objects.all().count())
        u = User.objects.get(username='presentindjango_admin')
        self.assertEqual(['g_membersdjango'], [x.name for x in u.groups.all()])
        u = User.objects.get(username='notadminindjango')
        self.assertEqual(['g_membersdjango'], [x.name for x in u.groups.all()])
