
Complete configuration
======================


Configuration options
---------------------

You can look current settings with the following command:

.. code-block:: bash

    multisync-manage config

Here is the complete list of settings:

.. code-block:: ini

  [database]
  engine = django.db.backends.sqlite3
  # SQL database engine, can be 'django.db.backends.[postgresql_psycopg2|mysql|sqlite3|oracle]'.
  host = 
  # Empty for localhost through domain sockets or "127.0.0.1" for localhost + TCP
  name = /home/mgallet/.virtualenvs/multisync/local/var/multisync/data/database.sqlite3
  # Name of your database, or path to database file if using sqlite3.
  password = 
  # Database password (not used with sqlite3)
  port = 
  # Database port, leave it empty for default (not used with sqlite3)
  user = 
  # Database user (not used with sqlite3)
  [global]
  admin_email = admin@localhost
  # error logs are sent to this e-mail address
  default_group = Users
  # Name of the default group for newly-created users.
  language_code = fr-fr
  # A string representing the language code for this installation.
  time_zone = Europe/Paris
  # A string representing the time zone for this installation, or None. 
  [ldap]
  base_dn = dc=test,dc=example,dc=org
  # base dn for searching users and groups, like dc=test,dc=example,dc=org.
  group_ou = ou=Groups
  # subtree containing groups, like ou=Groups
  name = ldap://192.168.56.101/
  # LDAP url, like ldap://127.0.0.1/ or ldapi:///
  password = toto
  # LDAP password to bind with
  user = cn=admin,dc=test,dc=example,dc=org
  # LDAP user name to bind with
  user_ou = ou=Users
  # subtree containing users, like ou=Users
  [multisync]
  synchronizer = multisync.django_synchronizers.DjangoSynchronizer
  [prosody]
  domain = im.example.org
  # Domain to append to the Prosody's usernames
  group_file = /home/mgallet/.virtualenvs/multisync/local/var/multisync/groups.ini
  # path of the generated Prosody config file. See `https://prosody.im/doc/modules/mod_groups#example` for more info.



If you need more complex settings, you can override default values (given in `djangofloor.defaults` and
`multisync.defaults`) by creating a file named `/home/multisync/.virtualenvs/multisync/etc/multisync/settings.py`.



Debugging
---------

If something does not work as expected, you can look at logs (in /var/log/supervisor if you use supervisor)
or try to run the server interactively:

.. code-block:: bash

  sudo service supervisor stop
  sudo -u multisync -i
  workon multisync
  multisync-manage config
  multisync-manage runserver
  multisync-gunicorn




Backup
------

A complete MultiSync installation is made a different kinds of files:

    * the code of your application and its dependencies (you should not have to backup them),
    * static files (as they are provided by the code, you can lost them),
    * configuration files (you can easily recreate it, or you must backup it),
    * database content (you must backup it),
    * user-created files (you must also backup them).

Many backup strategies exist, and you must choose one that fits your needs. We can only propose general-purpose strategies.

We use logrotate to backup the database, with a new file each day.

.. code-block:: bash

  sudo mkdir -p /var/backups/multisync
  sudo chown -r multisync: /var/backups/multisync
  sudo -u multisync -i
  cat << EOF > /home/multisync/.virtualenvs/multisync/etc/multisync/backup_db.conf
  /var/backups/multisync/backup_db.sql.gz {
    daily
    rotate 20
    nocompress
    missingok
    create 640 multisync multisync
    postrotate
    myproject-manage dumpdb | gzip > /var/backups/multisync/backup_db.sql.gz
    endscript
  }
  EOF
  touch /var/backups/multisync/backup_db.sql.gz
  crontab -e
  MAILTO=admin@localhost
  0 1 * * * /home/multisync/.virtualenvs/multisync/bin/multisync-manage clearsessions
  0 2 * * * logrotate -f /home/multisync/.virtualenvs/multisync/etc/multisync/backup_db.conf


Backup of the user-created files can be done with rsync, with a full backup each month:
If you have a lot of files to backup, beware of the available disk place!

.. code-block:: bash

  sudo mkdir -p /var/backups/multisync/media
  sudo chown -r multisync: /var/backups/multisync
  cat << EOF > /home/multisync/.virtualenvs/multisync/etc/multisync/backup_media.conf
  /var/backups/multisync/backup_media.tar.gz {
    monthly
    rotate 6
    nocompress
    missingok
    create 640 multisync multisync
    postrotate
    tar -C /var/backups/multisync/media/ -czf /var/backups/multisync/backup_media.tar.gz .
    endscript
  }
  EOF
  touch /var/backups/multisync/backup_media.tar.gz
  crontab -e
  MAILTO=admin@localhost
  0 3 * * * rsync -arltDE /home/mgallet/.virtualenvs/multisync/local/var/multisync/data/media/ /var/backups/multisync/media/
  0 5 0 * * logrotate -f /home/multisync/.virtualenvs/multisync/etc/multisync/backup_media.conf

Restoring a backup
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

  cat /var/backups/multisync/backup_db.sql.gz | gunzip | /home/multisync/.virtualenvs/multisync/bin/multisync-manage dbshell
  tar -C /home/mgallet/.virtualenvs/multisync/local/var/multisync/data/media/ -xf /var/backups/multisync/backup_media.tar.gz





Monitoring
----------


Nagios or Shinken
~~~~~~~~~~~~~~~~~

You can use Nagios checks to monitor several points:

  * connection to the application server (gunicorn or uwsgi):
  * connection to the database servers (PostgreSQL),
  * connection to the reverse-proxy server (apache or nginx),
  * the validity of the SSL certificate (can be combined with the previous check),
  * creation date of the last backup (database and files),
  * living processes for gunicorn, postgresql, apache,
  * standard checks for RAM, disk, swap…

Here is a sample NRPE configuration file:

.. code-block:: bash

  cat << EOF | sudo tee /etc/nagios/nrpe.d/multisync.cfg
  command[multisync_wsgi]=/usr/lib/nagios/plugins/check_http -H 127.0.0.1 -p 9000
  command[multisync_reverse_proxy]=/usr/lib/nagios/plugins/check_http -H localhost -p 80 -e 401
  command[multisync_backup_db]=/usr/lib/nagios/plugins/check_file_age -w 172800 -c 432000 /var/backups/multisync/backup_db.sql.gz
  command[multisync_backup_media]=/usr/lib/nagios/plugins/check_file_age -w 3024000 -c 6048000 /var/backups/multisync/backup_media.sql.gz
  command[multisync_gunicorn]=/usr/lib/nagios/plugins/check_procs -C python -a '/home/multisync/.virtualenvs/multisync/bin/multisync-gunicorn'
  EOF

Sentry
~~~~~~

For using Sentry to log errors, you must add `raven.contrib.django.raven_compat` to the installed apps.

.. code-block:: ini

  [global]
  extra_apps = raven.contrib.django.raven_compat
  [sentry]
  dsn_url = https://[key]:[secret]@app.getsentry.com/[project]

Of course, the Sentry client (Raven) must be separately installed, before testing the installation:

.. code-block:: bash

  sudo -u multisync -i
  multisync-manage raven test





LDAP groups
-----------

There are two possibilities to use LDAP groups, with their own pros and cons:

  * on each request, use an extra LDAP connection to retrieve groups instead of looking in the SQL database,
  * regularly synchronize groups between the LDAP server and the SQL servers.

The second approach can be used without any modification in your code and remove a point of failure
in the global architecture (if you allow some delay during the synchronization process).
A tool exists for such synchronization: `MultiSync <https://github.com/d9pouces/Multisync>`_.
