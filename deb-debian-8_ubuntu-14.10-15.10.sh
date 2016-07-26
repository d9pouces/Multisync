#!/bin/bash
set -e

# base packages
sudo apt-get update
sudo apt-get upgrade --yes
sudo apt-get install --yes vim dh-make ntp rsync liblzma-dev tree
sudo apt-get install --yes python-all-dev virtualenvwrapper \
    python-tz python-setuptools \
    python-oauthlib python-sqlparse \
    apache2 libapr1 libaprutil1 libaprutil1-dbd-sqlite3 libaprutil1-ldap gunicorn python-celery \
    python-medusa python-meld3 ssl-cert python-msgpack python-gunicorn
sudo apt-get install --yes python-ldap libldap2-dev libsasl2-dev python-futures
source /etc/bash_completion.d/virtualenvwrapper



# create the virtual env
set +e
mkvirtualenv -p `which python` djangofloor
workon djangofloor
pip install setuptools --upgrade
pip install pip --upgrade
pip install debtools djangofloor
set -e
python setup.py install



# generate packages for all dependencies
multideb -r -v -x stdeb-debian-8_ubuntu-14.10-15.10.cfg

# creating package for multisync
rm -rf `find * | grep pyc$`
python setup.py bdist_deb_django -x stdeb-debian-8_ubuntu-14.10-15.10.cfg
deb-dep-tree deb_dist/*deb
mv deb_dist/*deb deb



# install all packages
sudo dpkg -i deb/python-pyldap_*.deb
sudo dpkg -i deb/python-*.deb

set -e
