================
Pocket Connector
================

From Trigger Happy, this connector provides an access to your Pocket account to add/get notes

Requirements :
==============
* `django_th <https://github.com/foxmask/django-th>`_ == 0.9.0
* `pocket <https://pypi.python.org/pypi/pocket>`_  == 0.3.5


Installation:
=============
to get the project, from your virtualenv, do :

.. code:: python

    pip install django-th-pocket
    
then do

.. code:: python

    python manage.py syncdb

to startup the database

Parameters :
============
As usual you will setup the database parameters.

Important parts are the settings of the available services :

Settings.py 
-----------

INSTALLED_APPS
~~~~~~~~~~~~~~

add the module th_rss to INSTALLED_APPS

.. code:: python

    INSTALLED_APPS = (
        'th_pocket',
    )    


TH_SERVICES 
~~~~~~~~~~~

TH_SERVICES is a list of the services used by Trigger Happy

.. code:: python

    TH_SERVICES = (
        'th_pocket.my_pocket.ServicePocket',
    )


TH_POCKET
~~~~~~~~~
TH_POCKET is the settings you will need to be able to add/read data in/from Pocket.

.. code:: python

    TH_POCKET = {
        'consumer_key': 'abcdefghijklmnopqrstuvwxyz',
    }


Setting up : Administration
===========================

once the module is installed, go to the admin panel and activate the service Pocket. 

All you can decide here is to tell if the service requires an external authentication or not.

Once they are activated. User can use them.
