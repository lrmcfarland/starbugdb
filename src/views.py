#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Observation views

In this example, "home" is underloaded to be clear what goes where
when the base.html template uses home_blueprint.show_home to reference
obsui app.register_blueprint(views.home_page).

This gives a BuildError: Could not build url for endpoint
'home.home'. Did you mean 'home.show_home' instead?

if it is not aligned correctly.

"""

import flask


home_page = flask.Blueprint('home_blueprint', __name__, template_folder='templates')

# TODO requires login
@home_page.route('/')
def show_home():
    return flask.render_template('home.html')


# TODO requires login
@home_page.route("/record_observation")
def record_observation():
    return flask.render_template('record_observation.html')


# TODO requires login
@home_page.route("/show_observations")
def show_observations():
    return flask.render_template('show_observations.html')
