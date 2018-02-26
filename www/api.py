#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""obsevations api"""

import datetime
import flask
import flask_login
import flask_pymongo
import json
import re
import requests

import model

# ===================
# ===== globals =====
# ===================

# TODO until python3
timezone_re = re.compile('(?P<sign>[+-]*)(?P<hours>\d\d)(?P<mins>\d\d)')


api = flask.Blueprint('api', __name__, url_prefix='/api/v1')


# ===============
# ===== api =====
# ===============


@api.route("/info")
@flask_login.login_required
def info():
    """various database objects"""

    result = dict()

    try:

        result['db name'] = model.mongo.db.name

        users = list()
        for user in model.mongo.db.users.find():
            users.append('{}'.format(user))

        result['users'] = users

        collections = list()
        for collection in model.mongo.db.list_collections():
            collections.append('{}'.format(collection['name']))

        obs = model.mongo.db['observations']

        result['observation full name'] = '{}'.format(obs.full_name)

    except flask_pymongo.pymongo.errors.OperationFailure as err:
        result['error'] = str(err)

    return flask.jsonify(**result)


@api.route("/record_observation", methods=['GET', 'POST'])
@flask_login.login_required
def record_observation_api():
    """Record an observation

    Sets the schema for the observations table
    """

    result = dict()

    if flask.request.method == 'GET':
        result['error'] = 'Error POST required'
        return flask.jsonify(**result)


    try:

        obsdb = model.mongo.db['observations']

        obs = json.loads(flask.request.get_data())


        res = obsdb.insert({'iso8601': obs['iso8601'], # TODO datetime type
                            'observer':obs['observer'],
                            'latitude': float(obs['latitude']),
                            'longitude': float(obs['longitude']),
                            'target': obs['target'],
                            'ra': float(obs['ra']),
                            'dec': float(obs['dec']),
                            'notes': obs['notes'],
                        }
        )


        result['status'] = 'success %s' % res # TODO meh

    except (AttributeError, ValueError) as err:
        result['error'] = 'Error: {}.'.format(err)

    except flask_pymongo.pymongo.errors.OperationFailure as err:
        result['error'] = 'Operation Failure: {}'.format(err)

    return flask.jsonify(**result)


@api.route("/show_observations")
def show_observations_api():
    """Return observations for display

    TODO find criteria
    """

    result = {'data': list(), 'errors': list()}

    try:
        obsdb = model.mongo.db['observations']

        result['data'] = list()

        for obs in obsdb.find():
            try:
                result['data'].append({'observer':obs['observer'],
                                       'target':obs['target'],
                                       'iso8601':obs['iso8601'],
                                       'ra':  obs['ra'],
                                       'dec': obs['dec'],
                                       'notes': obs['notes']})
            except KeyError as err:
                result['errors'].append(str(err))

        result['status'] = 'success' # TODO meh

    except flask_pymongo.pymongo.errors.OperationFailure as err:
        result['error'] = str(err)

    return flask.jsonify(**result)


@api.route("/standardize")
def standardize():
    """Return starbug.com standard format of observation parameters

    For example, 30:30 to 30.5

    This is to store values as floats not strings.
    Uses AAI's api for parsing
    """

    result = dict()

    try:

        result['args'] = flask.request.args # {"alt":"30:30","az":"","date":"2018-02-26", ... "time":"20:32:30"},

        aai_result = requests.get('{}/api/v1/standardize'.format(flask.current_app.config['AAI_URI']), params=flask.request.args)
        result['standard'] = aai_result.json()

        result['AAI_URI'] = flask.current_app.config['AAI_URI']

    except Exception as err: # TODO be more specific

        # TODO log errors

        result['error'] = str(err)

    return flask.jsonify(**result)
