{% extends "djangofloor/dev/deb-debian-8_ubuntu-14.10-15.10.sh_tpl" %}
{% block extra_dependencies %}sudo apt-get install --yes python-ldap libldap2-dev libsasl2-dev python-futures
{% endblock %}