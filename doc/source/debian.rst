Debian Installation
===================

By default, MultiSync is only packaged as a standard Python project, downloadable from `Pypi <https://pypi.python.org>`_.
However, you can create pure Debian packages with `DjangoFloor <http://django-floor.readthedocs.org/en/latest/packaging.html#debian-ubuntu>`_.

The source code provides one Bash scripts,  `deb-debian-8_ubuntu-14.10-150.10.sh`.

This script is designed to run on basic installation and are split in five steps:

    * update system and install missing packages,
    * create a virtualenv and install all dependencies,
    * package all dependencies,
    * package MultiSync,
    * install all packages and MultiSync, prepare a simple configuration to test.

If everything is ok, you can copy all the .deb packages to your private mirror or to the destination server.
By default, MultiSync is installed with Apache 2.4 and systemd.
You can switch to Nginx or supervisor by tweaking the right `stdeb-XXX.cfg` file.


Configuration
-------------

Default configuration file is `/etc/multisync/settings.ini`.
If you need more complex settings, you can override default values (given in `djangofloor.defaults` and
`multisync.defaults`) by creating a file named `/etc/multisync/settings.py`.
After any change in the database configuration or any upgrade, you must migrate the database to create the required tables.

.. code-block:: bash

    sudo -u multisync multisync-manage migrate


After installation and configuration, do not forget to create a superuser:

.. code-block:: bash

    sudo -u multisync multisync-manage createsuperuser





Launch the service
------------------

The service can be stopped or started via the `service` command. By default, MultiSync is not started.

.. code-block:: bash

    sudo service multisync-gunicorn start


If you want MultiSync to be started at startup, you have to enable it in systemd:

.. code-block:: bash

    systemctl enable multisync-gunicorn.service




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
  cat << EOF > /etc/multisync/backup_db.conf
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
  0 1 * * * /usr/local/bin/multisync-manage clearsessions
  0 2 * * * logrotate -f /etc/multisync/backup_db.conf


Backup of the user-created files can be done with rsync, with a full backup each month:
If you have a lot of files to backup, beware of the available disk place!

.. code-block:: bash

  sudo mkdir -p /var/backups/multisync/media
  sudo chown -r multisync: /var/backups/multisync
  cat << EOF > /etc/multisync/backup_media.conf
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
  0 5 0 * * logrotate -f /etc/multisync/backup_media.conf

Restoring a backup
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

  cat /var/backups/multisync/backup_db.sql.gz | gunzip | /usr/local/bin/multisync-manage dbshell
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
  command[multisync_gunicorn]=/usr/lib/nagios/plugins/check_procs -C python -a '/usr/local/bin/multisync-gunicorn'
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




