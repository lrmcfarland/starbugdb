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


@home_page.route("/login", methods=['GET', 'POST'])
def login():
    """Authenticate to the mongo database.

    the return is to the authenticate() function in the login.html
    template javascript which completes the redirect
    """


    if flask.request.method == 'GET':
        return flask.render_template('login.html')

    try:

        user_creds = json.loads(flask.request.get_data())

        sbdb = model.mongo.db['users']

        found = sbdb.find_one({'email': user_creds['username']})
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

