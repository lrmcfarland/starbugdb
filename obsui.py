#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Flask UI for the starbug observation database

Assumes the databsae has been populated with conf/users.json

To run:

./obsui.py -p 8888 -d -l debug



==================================================

import bcrypt

I experimented with using bcrypt to store passwords. For example


  BCRYPT_SALT = '$2b$12$x06bwEbvN9K2fhsdu0bDS.' = bcrypt.gensalt()

  bcrypt.hashpw(flask.request.args.get('password').encode('utf-8'), BCRYPT_SALT)

  $2b$12$x06bwEbvN9K2fhsdu0bDS.5snXIp080hjHHEvMb/igrbcDH1Gk.ve

Where the salt is the first part of the hash. The idea is to store
the hash in the database and compare it to a hash of the input,
but the seed needs to be the same for this to work. It is part
the first part of the hash, so you can recover it from the saved
key.

But in this case I am using mongo to store the passwords. This secures
any interface, including mongo command line tools, e.g.

   $ mongo starbug -u starbug -p changeme3 --authenticationDatabase starbug

The problem with storing them myself means I needed to access a mongo
users table with hashed passwords before authenticating which seems to
be unnecessary exposure if mongo will store them for me.

I experimented with saving the hash in the flask config, like the
secret and while this will work, I don't think it is an improvement.
"""

import argparse
import bcrypt
import datetime
import flask
import flask_pymongo
import json
import logging
import logging.handlers
import re
import time

# ===================
# ===== globals =====
# ===================

_user_session_key = 'username'

timezone_re = re.compile('(?P<sign>.*)(?P<hours>\d\d)(?P<mins>\d\d)')

# TODO http://flask.pocoo.org/docs/0.12/patterns/appfactories/
# http://flask.pocoo.org/docs/0.12/config/

app = flask.Flask(__name__) # must be before decorators
app.config.from_pyfile('conf/obs-flask.cfg') # TODO hardcoded meh!
mongo = flask_pymongo.PyMongo(app)


# ===============
# ===== app =====
# ===============


class Error(Exception):
    pass


@app.route("/")
def home():
    """Starbug observations home"""

    app.logger.info('obs_username %s', flask.session.get(_user_session_key, None))

    if flask.session.get(_user_session_key, None) is None:
        return flask.render_template('login.html')
    else:
        return flask.render_template('home.html')


@app.route("/login")
def login():
    """login page"""

    return flask.render_template('login.html')


@app.route("/logout")
def logout():
    """logout page"""

    try:
        flask.session.pop(_user_session_key)
    except KeyError as err:
        app.logger.error('logout missing session key %s', err)

    return flask.redirect('/')


@app.route("/record_observation")
def record_observation():
    """Application's home"""
    return flask.render_template('record_observation.html')


@app.route("/show_observations")
def show_observations():
    """Application's home"""
    return flask.render_template('show_observations.html')


# ---------------
# ----- API -----
# ---------------

@app.route("/api/v1/info")
def info_api():
    """various database objects"""

    app.logger.error('info called with request: %s', flask.request.args.to_dict())

    result = dict()

    result['db name'] = mongo.db.name

    try:

        app.logger.info('mongo.db.name: %s', mongo.db.name) # TODO rm

        app.logger.info('%s collections', mongo.db.name) # TODO rm

        app.logger.info('flask.session: %s', flask.session) # TODO rm exposes password!
        # flask.session: <SecureCookieSession {u'obs_user': u'starbug',
        # u'obs_username': u'guest', u'obs_password': u'changeme3'}>

        for user in mongo.db.users.find():
            app.logger.info('\tuser %s', user)

        if False:
            for collection in mongo.db.list_collections():
                app.logger.info('\t%s', collection['name']) # TODO rm

        obs = mongo.db['observations']

        app.logger.debug('obs.full_name: %s', obs.full_name) # TODO rm?

        app.logger.debug('obs.name: %s', obs.name)

    except flask_pymongo.pymongo.errors.OperationFailure as err:
        app.logger.error('info error: %s', err)
        result['error'] = str(err)


    return flask.jsonify(**result)


# TODO? @app.route("/api/v1/login", methods=['POST'])
@app.route("/api/v1/login")
def login_api():
    """Authenticate to the mongo database.

    This uses mongodbs authentication mechanism to store
    passwords. See note about bcrypt in the header

    """

    app.logger.info('login called for user: %s', flask.request.args.get('username'))

    result = dict()

    try:

        sbdb = mongo.db['users']

        found = sbdb.find({'username': flask.request.args.get('username')})

        if found.count() == 0:
            raise Error('user "{}" does not exist'.format(flask.request.args.get('username')))

        if found.count() > 1:
            raise Error('user "{}" exists multiple times'.format(flask.request.args.get('username')))

        a_user = found.next()

        # TODO use bcrypt
        if not bcrypt.checkpw(flask.request.args.get('password').encode('utf-8'), a_user['password'].encode('utf-8')):
            raise Error('authentication failed')

        flask.session[_user_session_key] = {'username': a_user['username'],
                                            'write': a_user['write']} # omit mongo id: is not JSON serializable

    except (Error, KeyError, flask_pymongo.pymongo.errors.OperationFailure) as err:
        app.logger.error('login error: %s', err)
        result['error'] = str(err)
        return flask.jsonify(**result)


    result['success'] = 'successful login'

    return flask.jsonify(**result)


# TODO? @app.route("/api/v1/record_observation", methods=['POST'])
@app.route("/api/v1/record_observation")
def record_observation_api():
    """TODO POST?

    http://werkzeug.pocoo.org/docs/0.12/datastructures/#werkzeug.datastructures.MultiDict.to_dict

    TODO use aai /api/v1/lat,lon,dec,ra2decimal, /api/v1/datetime2iso8601
         python3 for timezone? or coords.datemtime

    TODO python3 supports timezone %z, this is a work around
    TODO decimal time, fractional timezones
    TODO use aai api to parse
    """

    app.logger.error('record observation called with request: %s', flask.request.args.to_dict())

    result = dict()

    try:

        obs = flask.request.args.to_dict()
        as_iso8601 = ''.join([obs['date'], 'T', obs['time']])

        # TODO regex
        if '.' in as_iso8601:
            obs_datetime = datetime.datetime.strptime(as_iso8601, '%Y-%m-%dT%H:%M:%S.%f') # decimal seconds
        else:
            obs_datetime = datetime.datetime.strptime(as_iso8601, '%Y-%m-%dT%H:%M:%S')

        tz_found = timezone_re.match(obs['timezone'])
        if not tz_found:
            result['error'] ='timezone {} is in an unsupported format. It must be [+/-]hhmm'.format(obs['timezone'])
            app.logger.error(result['error'])
            return flask.jsonify(**result)

        obs_datetime += datetime.timedelta(hours=int(obs['timezone']))

        obs['datetime'] = obs_datetime

        obsdb = mongo.db['observations']

        # TODO use mongodb roles?
        if not flask.session[_user_session_key]['write']:
            raise Error('user {} does not have write permission'.format(flask.session[_user_session_key]['username']))

        res = obsdb.insert(obs)

        result['status'] = 'success %s' % res # TODO meh
        app.logger.error('result: %s', res)

    except (Error, ValueError) as err:
        result['error'] = 'Error: {}.'.format(err)
        app.logger.error(result['error'])

    except flask_pymongo.pymongo.errors.OperationFailure as err:
        result['error'] = 'Operation Failure: {}\nTry logging out and in again.'.format(err)
        app.logger.error('Operation Failure record_observation_api(): %s', err)

    return flask.jsonify(**result)


@app.route("/api/v1/show_observations")
def show_observations_api():
    """Return observations for display

    TODO find criteria
    """

    app.logger.info('show observation called with request: %s', flask.request.args.to_dict())

    result = dict()

    try:
        obsdb = mongo.db['observations']

        result['data'] = list()

        for obs in obsdb.find():
            try:
                result['data'].append({'name':obs['target_name'],
                                       'date':obs['date'],
                                       'time':obs['time'],
                                       'ra':  obs['ra'],
                                       'dec': obs['dec'],
                                       'notes': obs['notes']})
            except KeyError as err:
                app.logger.error('skipping %s. %s', obs, err)

        result['status'] = 'success' # TODO meh

    except flask_pymongo.pymongo.errors.OperationFailure as err:
        app.logger.error('auth error: %s\nTry logging out and in again.', err)
        result['error'] = str(err)

    return flask.jsonify(**result)


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
                'loglevel': 'debug',
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
