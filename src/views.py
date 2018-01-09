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

import bcrypt
import flask
import flask_login
import flask_pymongo
import json

import model
import user


home_page = flask.Blueprint('home_blueprint', __name__, template_folder='templates')


class Error(Exception):
    pass


@home_page.route('/')
def show_home():
    return flask.render_template('home.html')


@home_page.route("/record_observation")
@flask_login.login_required
def record_observation():
    return flask.render_template('record_observation.html')


@home_page.route("/show_observations", methods=['GET', 'POST'])
def show_observations():
    return flask.render_template('show_observations.html')


@home_page.route("/login", methods=['GET', 'POST'])
def login():
    """Authenticate to the mongo database"""

    if flask.request.method == 'GET':
        return flask.render_template('login.html')

    try:

        user_creds = json.loads(flask.request.get_data())

        found = model.mongo.db['users'].find_one({'email': user_creds['username']})
        if not found:
            raise Error('no user {}'.format(user_creds['username']))

        a_user = user.User(**found)

        if not bcrypt.checkpw(user_creds['password'].encode('utf-8'), a_user.password.encode('utf-8')):
            raise Error('authentication failed')

        flask_login.login_user(a_user)

        return flask.request.args.get('next') or flask.url_for('home_blueprint.record_observation')

    except (Error, AttributeError, KeyError, flask_pymongo.pymongo.errors.OperationFailure) as err:
        flask.flash('{}'.format(err))
        return flask.url_for('home_blueprint.login')

    return flask.render_template('login.html')


@home_page.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('home_blueprint.login'))
