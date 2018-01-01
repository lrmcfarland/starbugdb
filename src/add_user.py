#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Adds users to mongodb with bcrypt hashed passwords




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
                               args.username,
                               args.password,
                               roles=users[user]['create_args']['roles'])


        print(users[user])


"""

import argparse
import bcrypt
import json
import pymongo


class Error(Exception):
    pass


if __name__ == '__main__':

    defaults = {'host':'localhost',
                'port': 27017,
                'admin_name': 'admin',
                'admin_password': 'changeme',
                'can write': False
    }

    parser = argparse.ArgumentParser(description='add users with bcrypt-ed passwords')

    parser.add_argument('--host', type=str, dest='host', default=defaults['host'],
                        metavar='host',
                        help='host IP to serve (default: %(default)s)')

    parser.add_argument('--port', type=int, dest='port', default=defaults['port'],
                        help='port (default: %(default)s)')

    parser.add_argument('--admin-name', type=str, dest='admin_name',
                        default=defaults['admin_name'], metavar='admin_name', help='admin name (default: %(default)s)')

    parser.add_argument('--admin-password', type=str, dest='admin_password',
                        default=defaults['admin_password'], metavar='password', help='admin password  (default: %(default)s)')

    parser.add_argument('-u', '--username', type=str, dest='username', required=True,
                        metavar='username', help='user name')

    parser.add_argument('-p', '--password', type=str, dest='password', required=True,
                        metavar='password', help='user password')

    parser.add_argument('-w', '--write', action='store_true',
                        dest='write', default=defaults['can write'],
                        help='user has write privileges (default: %(default)s)')

    args = parser.parse_args()


    # ----- add user -----

    try:

        client = pymongo.MongoClient(args.host, args.port)

        client.admin.authenticate(args.admin_name, args.admin_password)

        users = client['starbug']['users']

        # check user doesn't already exist, TODO mongo to enforce unique index on name?

        found = users.find({'username': args.username})
        if found.count():
            raise Error('user {} already exists'.format(args.username))

        users.insert({'username': args.username,
                      'password': args.password, # TODO bcrypt
                      'write': args.write})

    except (Error, pymongo.errors.OperationFailure, pymongo.errors.ServerSelectionTimeoutError) as err:

        print('{}'.format(err))


    print('users')
    for user in users.find():
        print('user: {}'.format(user)) # TODO hmm

print('done')
