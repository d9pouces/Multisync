# -*- coding: utf-8 -*-
"""Setup file for the MultiSync project.
"""

import codecs
import os.path
import re
from setuptools import setup, find_packages

# avoid a from multisync import __version__ as version
# (that compiles multisync.__init__ and is not compatible with bdist_deb)
version = None
for line in codecs.open(os.path.join('multisync', '__init__.py'), 'r', encoding='utf-8'):
    matcher = re.match(r"""^__version__\s*=\s*['"](.*)['"]\s*$""", line)
    version = version or matcher and matcher.group(1)

# get README content from README.md file
with codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as fd:
    long_description = fd.read()

entry_points = {'console_scripts': ['multisync-manage = djangofloor.scripts:manage',
                                    'multisync = multisync.command:main', ]}

setup(name='multisync',
      version=version,
      description='No description yet.',
      long_description=long_description,
      author='Matthieu Gallet',
      author_email='github@19pouces.net',
      license='CeCILL-B',
      url='',
      entry_points=entry_points,
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='multisync.tests',
      install_requires=['djangofloor', 'django-ldapdb', ],
      setup_requires=[],
      classifiers=[], )
