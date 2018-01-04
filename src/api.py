#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""obsevations api"""

import datetime
import flask
import flask_pymongo
import re

import model

# ===================
# ===== globals =====
# ===================

# TODO until python3
timezone_re = re.compile('(?P<sign>.*)(?P<hours>\d\d)(?P<mins>\d\d)')


api = flask.Blueprint('api', __name__, url_prefix='/api/v1')


# ===============
# ===== api =====
# ===============


# TODO requiers login
@api.route("/info")
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


# TODO requiers login
# TODO? @api.route("/record_observation", methods=['POST'])
@api.route("/record_observation")
def record_observation_api():
    """TODO POST?

    http://werkzeug.pocoo.org/docs/0.12/datastructures/#werkzeug.datastructures.MultiDict.to_dict

    TODO use aai /lat,lon,dec,ra2decimal, /datetime2iso8601
         python3 for timezone? or coords.datemtime

    TODO python3 supports timezone %z, this is a work around
    TODO decimal time, fractional timezones
    TODO use aai api to parse
    """

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
            return flask.jsonify(**result)

        obs_datetime += datetime.timedelta(hours=int(obs['timezone']))

        obs['datetime'] = obs_datetime

        obsdb = model.mongo.db['observations']

        res = obsdb.insert(obs)

        result['status'] = 'success %s' % res # TODO meh

    except ValueError as err:
        result['error'] = 'Error: {}.'.format(err)

    except flask_pymongo.pymongo.errors.OperationFailure as err:
        result['error'] = 'Operation Failure: {}'.format(err)

    return flask.jsonify(**result)


@api.route("/show_observations")
def show_observations_api():
    """Return observations for display

    TODO find criteria
    """

    result = dict()

    try:
        obsdb = model.mongo.db['observations']

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
                result['data'] = str(err)

        result['status'] = 'success' # TODO meh

    except flask_pymongo.pymongo.errors.OperationFailure as err:
        result['error'] = str(err)

    return flask.jsonify(**result)
