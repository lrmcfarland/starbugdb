#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Flask UI for the starbug observation database

To run:

./obsui.py -p 8888 -d -l debug

Use src/add_user.py to add users to test with.
"""

import argparse
import flask
import logging
import logging.handlers

import api
import model
import views


# ===================
# ===== globals =====
# ===================


# TODO http://flask.pocoo.org/docs/0.12/patterns/appfactories/
# http://flask.pocoo.org/docs/0.12/config/


app = flask.Flask(__name__)

app.config.from_pyfile('conf/obs-flask.cfg') # TODO hardcoded meh!

model.mongo.init_app(app)

app.register_blueprint(views.home_page)

app.register_blueprint(api.api)


# ================
# ===== main =====
# ================

if __name__ == "__main__":

    """Run stand alone in flask"""


    loglevels = {'debug': logging.DEBUG,
                 'info': logging.INFO,
                 'warn': logging.WARN,
                 'error': logging.ERROR}


    loghandlers = {'stream': 'stream',
                   'rotating': 'rotating'}


    defaults = {'debug': False,
                'host':'0.0.0.0',
                'logfilename': '/opt/starbug.com/logs/flask',
                'loghandler': 'stream',
                'loglevel': 'warn',
                'port': 8080,
    }


    parser = argparse.ArgumentParser(description='starbug observations database flask server')

    parser.add_argument('-d', '--debug', action='store_true',
                        dest='debug', default=defaults['debug'],
                        help='flask debug (default: %(default)s)')

    parser.add_argument('--host', type=str, dest='host', default=defaults['host'],
                        metavar='host',
                        help='host IP to serve (default: %(default)s)')

    parser.add_argument('--logfilename', type=str, dest='logfilename', default=defaults['logfilename'],
                        metavar='logfilename',
                        help='name of log file (default: %(default)s)')

    parser.add_argument('--loghandler', choices=list(loghandlers.keys()),
                        dest='loghandler', default=defaults['loghandler'],
                        metavar='HANDLER',
                        help='logging handler choice: %(keys)s (default: %(default)s)' % {
                            'keys':', '.join(list(loghandlers.keys())), 'default':'%(default)s'})

    parser.add_argument('-l', '--loglevel', choices=list(loglevels.keys()),
                        dest='loglevel', default=defaults['loglevel'],
                        metavar='LEVEL',
                        help='logging level choice: %(keys)s (default: %(default)s)' % {
                            'keys':', '.join(list(loglevels.keys())), 'default':'%(default)s'})

    parser.add_argument('-p', '--port', type=int, dest='port', default=defaults['port'],
                        help='port (default: %(default)s)')

    args = parser.parse_args()



    # ----- set up logging -----

    if args.loghandler == 'stream':

        log_handler = logging.StreamHandler()

    elif args.loghandler == 'rotating':

        log_handler = logging.handlers.RotatingFileHandler(args.logfilename,
                                                           maxBytes=1000000,
                                                           backupCount=10) # TODO from cli

    else:
        parser.error('unsupported log handler %s', args.loghandler)


    log_handler.setFormatter(
        logging.Formatter(
            '[%(asctime)s %(levelname)s %(filename)s %(lineno)s] %(message)s'))

    app.logger.addHandler(log_handler)
    app.logger.setLevel(loglevels[args.loglevel])

    # -------------------
    # ----- run app -----
    # -------------------

    app.run(host=args.host, port=args.port, debug=args.debug)
