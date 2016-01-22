MultiSync
=========

Python script for copying users and groups from a read-only LDAP to several kinds of websites using the Django's ORM.

Currently, synchronization systems are provided for:

  * the Django default authentication classes (:class:`django.contrib.auth.models.User` and 
  :class:`django.contrib.auth.models.Group`),
  * the Prosody group system (generates plain config file),
  * the PenatesServer groups and users bases (based on the Django's classes).

You only have to provide a configuration file for the application to synchronize and to run `MultiSync` in a crontab (or manually if you prefer).
The expeccted LDAP model is currently tied to the one provided by the `Penates <https://github.com/d9pouces/Penates>`,
 but you can easily override it.


The default system is extensible and more synchronizers can easily be added.
More generally, MultiSync relies on a class to synchronize a set of objects against a reference set of objects of same kind,
and you must implement a few virtual methods for each kind a synchronized website.

