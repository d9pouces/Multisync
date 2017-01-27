# -*- coding=utf-8 -*-
from __future__ import unicode_literals

import os

from djangofloor.deb_fixes import file_replace

__author__ = 'mgallet'


# noinspection PyUnusedLocal
def remove_unicode_literals(package_name, package_version, deb_src_dir):
    if os.path.isfile('setup.py'):
        file_replace('setup.py', 'from __future__ import unicode_literals', '')
