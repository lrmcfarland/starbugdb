#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Flask UI for the starbug observation database

The default config file config/obsui.py is for running inside a
container with mongod running as starbugdb_00.

To Run with the AAI on the local host

./obsui.py -c config/obsui_flask_localhost.py

with aai.starbug.com

./obsui.py -c config/obsui_flask_starbug.py


Reference:

    http://flask.pocoo.org/docs/0.12/patterns/appfactories/
    http://flask.pocoo.org/docs/0.12/config/

"""

import argparse
import bson
import flask
import flask_login
import logging
import os

import api
import model
import user
import views

# =================
# ===== login =====
# =================

login_manager = flask_login.login_manager.LoginManager()
login_manager.login_view = 'home_blueprint.login'

@login_manager.user_loader
def load_user(user_id):
    """load manager user loader"""
    users = model.mongo.db['users']
    found = users.find_one({'_id': bson.objectid.ObjectId(user_id)})
    if found:
        return user.User(**found)
    return None


# ===================
# ===== factory =====
# ===================


def factory(a_config_flnm=None):
    """Creates a observations ui flask

    Blueprints makes this much clearer

    Args:
        a_config_flnm (str): configuration filename


    Returns a reference to the flask app
    """

    config_key = 'OBSUI_FLASK_CONFIG'

    if a_config_flnm is not None:
        config_flnm = a_config_flnm

    elif os.getenv(config_key) is not None:
        config_flnm = os.environ[config_key]

    else:
        config_flnm = 'config/obsui-flask-testing-config.py'
        logging.warning('Using Observation UI default configuration %s.', config_flnm)


    obsui_app = flask.Flask(__name__)

    obsui_app.config.from_pyfile(config_flnm)

    model.mongo.init_app(obsui_app)

    obsui_app.register_blueprint(views.home_page)
    obsui_app.register_blueprint(api.api)

    login_manager.init_app(obsui_app)

    return obsui_app


# ================
# ===== main =====
# ================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='starbug observations database flask server')

    parser.add_argument('-c', '--config', type=str, dest='config', default=None,
                        metavar='config',
                        help='The name of the flask config pyfile.')

    args = parser.parse_args()

    # -------------------
    # ----- run app -----
    # -------------------

    app = factory(args.config)

    app.run()
