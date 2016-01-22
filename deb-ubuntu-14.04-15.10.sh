#!/bin/bash

# base packages
sudo apt-get update
sudo apt-get upgrade --yes
sudo apt-get install --yes vim dh-make ntp rsync liblzma-dev tree
sudo apt-get install --yes python-all-dev virtualenvwrapper python-tz python-setuptools apache2  libapr1 libaprutil1 libaprutil1-dbd-sqlite3 libaprutil1-ldap python-medusa python-meld3 ssl-cert
source /etc/bash_completion.d/virtualenvwrapper



# create the virtual env
mkvirtualenv -p `which python` djangofloor
workon djangofloor
pip install setuptools --upgrade
pip install pip --upgrade
pip install debtools djangofloor
python setup.py install



# generate packages for all dependencies
multideb -r -v -x stdeb-ubuntu-14.04-15.10.cfg

# creating package for multisync
rm -rf `find * | grep pyc$`
python setup.py bdist_deb_django -x stdeb-ubuntu-14.04-15.10.cfg
deb-dep-tree deb_dist/*deb
mv deb_dist/*deb deb



# install all packages
sudo dpkg -i deb/python-*.deb

# package configuration
IP=`/sbin/ifconfig | grep -Eo 'inet (addr:|adr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'`
sudo sed -i "s/localhost/$IP/g" /etc/apache2/sites-available/multisync.conf
sudo sed -i "s/localhost/$IP/g" /etc/multisync/settings.ini
sudo a2ensite multisync.conf
sudo a2dissite 000-default.conf
sudo -u multisync multisync-manage migrate
sudo service supervisor restart
sudo service apache2 restart

