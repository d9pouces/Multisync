Installation
============

Like many Python packages, you can use several methods to install MultiSync.
MultiSync designed to run with python2.7.x.
The following packages are also required:

  * setuptools >= 3.0
  * djangofloor >= 0.18.0


Of course you can install it from the source, but the preferred way is to install it as a standard Python package, via pip.


Installing or Upgrading
-----------------------

Here is a simple tutorial to install MultiSync on a basic Debian/Linux installation.
You should easily adapt it on a different Linux or Unix flavor.


Database
--------

You should not have to create a user or a database for MultiSync since its role is to reuse the database/tables of an
existing application.
MultiSync is able to deal with all standard Django database servers: PostgreSQL, SQLite, MySQL or OracleDB.





Application
-----------

Now, it's time to install MultiSync. In this example, we create a dedicated user, but you probably
want to reuse the same user as the application to synchronize: that allows MultiSync to access to the same config' file
since this file should not be readable by other users.

.. code-block:: bash

    sudo mkdir -p /home/mgallet/.virtualenvs/multisync/local/var/multisync
    sudo adduser --disabled-password multisync
    sudo chown multisync:www-data /home/mgallet/.virtualenvs/multisync/local/var/multisync
    sudo apt-get install virtualenvwrapper python2.7 python2.7-dev build-essential postgresql-client libpq-dev
    # application
    sudo -u multisync -i
    mkvirtualenv multisync -p `which python2.7`
    workon multisync
    pip install setuptools --upgrade
    pip install pip --upgrade
    pip install multisync psycopg2 gevent
    mkdir -p $VIRTUAL_ENV/etc/multisync
    cat << EOF > $VIRTUAL_ENV/etc/multisync/settings.ini
    [database]
    engine = django.db.backends.sqlite3
    host = 
    name = /home/mgallet/.virtualenvs/multisync/local/var/multisync/data/database.sqlite3
    password = 
    port = 
    user = 
    [global]
    admin_email = admin@localhost
    default_group = Users
    language_code = fr-fr
    time_zone = Europe/Paris
    [ldap]
    base_dn = dc=test,dc=example,dc=org
    group_ou = ou=Groups
    name = ldap://192.168.56.101/
    password = toto
    user = cn=admin,dc=test,dc=example,dc=org
    user_ou = ou=Users
    [multisync]
    synchronizer = multisync.django_synchronizers.DjangoSynchronizer
    [prosody]
    domain = im.example.org
    group_file = /home/mgallet/.virtualenvs/multisync/local/var/multisync/groups.ini
    EOF

Crontab
-------
MultiSync is designed to be launched via a crontab script or as Nagios check.





