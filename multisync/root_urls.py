# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

__author__ = 'Matthieu Gallet'


urls = [
    ('^index$', 'multisync.views.index'),
    
]

if __name__ == '__main__':
    import doctest
    doctest.testmod()