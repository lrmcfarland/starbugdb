#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Flask UI for the starbug observation database

The default config file conf/obsui.cfg is for running inside a
container with mongod running as starbugdb_00.

To test from the local command line, setup a vurtial environment:

source py3env/bin/activate

And run:

./obsui.py -d -f conf/obsui_localhost.cfg

with aai.starbug.com

./obsui.py -d -f conf/obsui_starbug.cfg


Reference:

    http://flask.pocoo.org/docs/0.12/patterns/appfactories/
    http://flask.pocoo.org/docs/0.12/config/

"""

import argparse
import bson
import flask
import flask_login
import logging
import logging.handlers

import api
import model
import user
import views

# =====================
# ===== utilities =====
# =====================

# TODO like model.mongo?
login_manager = flask_login.login_manager.LoginManager()
login_manager.login_view = 'home_blueprint.login'


def factory(conf_flnm):
    """Creates a observations ui flask

    Blueprints makes this much clearer

    Args:
        conf_flnm (str): configuration filename


    Returns a reference to the flask app
    """

    obsui_app = flask.Flask(__name__)
    obsui_app.config.from_pyfile(conf_flnm)

    model.mongo.init_app(obsui_app)

    obsui_app.register_blueprint(views.home_page)
    obsui_app.register_blueprint(api.api)

    login_manager.init_app(obsui_app)

    return obsui_app


@login_manager.user_loader
def load_user(user_id):
    """load manager user loader"""
    users = model.mongo.db['users']
    found = users.find_one({'_id': bson.objectid.ObjectId(user_id)})
    if found:
        return user.User(**found)
    return None


# ================
# ===== main =====
# ================

if __name__ == "__main__":

    defaults = {'config': 'conf/obsui_starbug.cfg',
                'debug': False,
                'host':'0.0.0.0',
                'port': 8090}


    parser = argparse.ArgumentParser(description='starbug observations database flask server')

    parser.add_argument('-f', '--config', type=str, dest='config', default=defaults['config'],
                        metavar='config',
                        help='name of config file (default: %(default)s)')

    parser.add_argument('-d', '--debug', action='store_true',
                        dest='debug', default=defaults['debug'],
                        help='flask debug (default: %(default)s)')

    parser.add_argument('--host', type=str, dest='host', default=defaults['host'],
                        metavar='host',
                        help='host IP to serve (default: %(default)s)')

    parser.add_argument('-p', '--port', type=int, dest='port', default=defaults['port'],
                        help='port (default: %(default)s)')

    args = parser.parse_args()

    # -------------------
    # ----- run app -----
    # -------------------

    app = factory(args.config)

    app.run(host=args.host, port=args.port, debug=args.debug)
