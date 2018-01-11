#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Starbug mongodb instance

http://flask.pocoo.org/docs/0.12/patterns/appfactories/#factories-extensions

http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Metaprogramming.html#intercepting-class-creation

http://flask.pocoo.org/docs/0.12/extensiondev/

# TODO singleton?

"""

import flask_pymongo


mongo = flask_pymongo.PyMongo()

