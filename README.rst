flask-cachebuster
========================================

Flask-CacheBuster is a lightweight http://flask.pocoo.org/ extension that adds a hash to the URL query parameters of each static file. This lets you safely declare your static resources as indefinitely cacheable because they automatically get new URLs when their contents change.

Notes:
=========
Inspired by https://github.com/ChrisTM/Flask-CacheBust, and an updated version of https://github.com/daxlab/Flask-Cache-Buster to work with python 3.+

Installation
============

Using pip::

  pip install flask-cachebuster

Usage
----------
Configuration::


  from flask_cachebuster import CacheBuster

  config = { 'extensions': ['.js', '.css', '.csv'], 'hash_size': 5 }

  cache_buster = CacheBuster(config=config)

  cache_buster.init_app(app)

Configuration
-------------------

Configuration::

* extensions - file extensions to bust
* hash_size - number of characters in hash

The http://flask.pocoo.org/docs/0.12/api/#flask.url_for function will now cache-bust your static files. For example, this template::

<script src="{{ url_for('static', filename='js/main.js') }}"></script>

will render like this::

<script src="/static/js/main.js?%3Fq%3Dc5b5b2fa19"></script>

