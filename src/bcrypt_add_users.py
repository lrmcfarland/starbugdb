#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Adds users to mongodb with bcrypt hashed passwords

Depreciated: I experimented with using bcrypt to store passwords. For example


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

Reads a JSON config file of users with mongo roles

http://api.mongodb.com/python/current/api/pymongo/database.html

WARNING: "Will change the password if user name already exists."

Picked off has from output
--------------------
{u'create_args': {u'pwd': u'changeme3', u'user': u'starbug', u'roles': [{u'db': u'starbug', u'role': u'dbAdmin'}, {u'db': u'starbug', u'role': u'readWrite'}]}, u'db': u'starbug'}
{u'create_args': {u'pwd': '$2b$12$xdO6EQ4JQp5TIxCY9QEVIumYclWGpzS/UKZt/6HvKgfcbm2i.6J9m', u'user': u'starbug', u'roles': [{u'db': u'starbug', u'role': u'dbAdmin'}, {u'db': u'starbug', u'role': u'readWrite'}]}, u'db': u'starbug'}
--------------------

works with escapes before adding bcrypt to server

$ mongo starbug -u starbug -p \$2b\$12\$xdO6EQ4JQp5TIxCY9QEVIumYclWGpzS\/UKZt\/6HvKgfcbm2i.6J9m --authenticationDatabase starbug
MongoDB shell version v3.4.10
connecting to: mongodb://127.0.0.1:27017/starbug
MongoDB server version: 3.4.10



> show tables
observations

> db.observations.find()
{ "_id" : ObjectId("5a447f24b682b6330eaf1cf5"), "target_name" : "Saturn", "dst" : "false", "longitude" : "-122.08224869375717", "datetime" : ISODate("2013-04-12T18:05:00Z"), "date" : "2013-05-11", "ra" : "14:31:18.2", "time" : "22:05:00", "latitude" : "37.40013480873489", "timezone" : "-0700", "dec" : "-11:54:56", "notes" : "First light Celestron NexStar 8SE" }

"""

import argparse
import bcrypt
import json
import pymongo



if __name__ == '__main__':

    defaults = {'host':'localhost',
                'port': 27017
    }

    parser = argparse.ArgumentParser(description='add users with bcrypt-ed passwords')

    parser.add_argument('--host', type=str, dest='host', default=defaults['host'],
                        metavar='host',
                        help='host IP to serve (default: %(default)s)')

    parser.add_argument('-f', '--config-filename', type=str, dest='config_filename', required=True,
                        metavar='config_filename', help='name of log file (default: %(default)s)')

    parser.add_argument('-p', '--port', type=int, dest='port', default=defaults['port'],
                        help='port (default: %(default)s)')

    args = parser.parse_args()

    # ----- set up logging -----

    client = pymongo.MongoClient('{}:{}'.format(args.host, args.port))

    client.admin.authenticate('admin', 'changeme')

    users = json.load(open(args.config_filename))

    for user in users:

        print('-'*20) # linefeed

        print(users[user]) # TODO rm
        bcrypt_salt = bcrypt.gensalt()

        print('bcrypt salt {}'.format(bcrypt_salt)

        users[user]['create_args']['pwd'] = bcrypt.hashpw(
            users[user]['create_args']['pwd'].encode('utf-8'), bcrypt_salt)

        # add_user is depreciated
        # client.starbug.add_user(users[user]['create_args']['user'],
        #                        users[user]['create_args']['pwd'],
        #                        roles=users[user]['create_args']['roles'])


        client.starbug.command('createUser',
                               users[user]['create_args']['user'],
                               users[user]['create_args']['pwd'],
                               roles=users[user]['create_args']['roles'])


        print(users[user])
