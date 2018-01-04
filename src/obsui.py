#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Flask UI for the starbug observation database

The default config file conf/obs-flask.cfg is for running inside a
container with mongod running as starbugdb-00.

To test from the local command line:

./obsui.py -p 8888 -d -f conf/obs-flask-localhost.cfg


Reference:

    http://flask.pocoo.org/docs/0.12/patterns/appfactories/
    http://flask.pocoo.org/docs/0.12/config/

"""

import argparse
import flask
import logging
import logging.handlers

import api
import model
import views

# =====================
# ===== utilities =====
# =====================

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

    return obsui_app


# ================
# ===== main =====
# ================

if __name__ == "__main__":

    """Run stand alone in flask"""

    defaults = {'config': 'conf/obs-flask.cfg',
                'debug': False,
                'host':'0.0.0.0',
                'port': 8080}


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
