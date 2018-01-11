#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Defines the user class.

__main__ adds users to mongodb with bcrypt hashed passwords

"""

import argparse
import bcrypt
import json
import pymongo


class Error(Exception):
    pass


class User(object):
    """Flask-Login User class"""

    def __init__(self, _id=0, username=None, password=None, authenticated=True, active=True, anon=False):

        """Matches records in starbug.users table.

        TODO email

        _id is intended for mongo's generated id

        > db.users.insert({"username": "lrm@starbug.com", "password": "changeme", "authenticated":false, "active":false, "anon":false})


        Args
            _id (unicode): unicode id, used by the login manager too
            username (str):   user's username as username
            password (str): user's password

            authenticated (bool): an authentication state
            active (bool):  an active state
            anon (bool): an anonymous state
        """

        self._id = _id
        self.username = username
        self.password = password
        self.authenticated = authenticated
        self.active = active
        self.anon = anon

        return


    def __str__(self):
        return '({_id}, {username}, ********, {authenticated}, {active}, {anon})'.format(**self.__dict__)


    def __repr__(self):
        return r'{{ {username}, "password": {password}, "authenticated":{authenticated}, "active":{active}, "anon":{anon} }}'.format(**self.__dict__)


    def get_id(self):
        """for the flask login manager"""
        return unicode(self._id)


    def for_insert(self):
        """Returns a dictionary for mongodb insert, i.e. no _id"""
        return {'username': self.username,
                'password': self.password,
                'authenticated': self.authenticated,
                'active': self.active,
                'anon': self.anon}


    @property
    def is_authenticated(self):
        return self.authenticated


    @property
    def is_active(self):
        return self.active


    @property
    def is_anonymous(self):
        return self.anon


# ================
# ===== main =====
# ================


if __name__ == '__main__':

    defaults = {'host':'localhost',
                'port': 27017,
                'admin_name': 'admin',
                'admin_password': 'changeme'
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
                        metavar='username', help='user username')

    parser.add_argument('-p', '--password', type=str, dest='password', required=True,
                        metavar='password', help='user password')


    args = parser.parse_args()

    # TODO rm user, deactiveate, anon?

    # ----- add user -----

    try:

        client = pymongo.MongoClient(args.host, args.port)

        client.admin.authenticate(args.admin_name, args.admin_password)

        users = client['starbug']['users']

        found = users.find_one({'username': args.username})
        if found:
            a_user = User(**found)
            raise Error('user {} already exists'.format(a_user))

        a_user = User(username=args.username, password = bcrypt.hashpw(args.password.encode('utf-8'), bcrypt.gensalt()))

        users.insert(a_user.for_insert())

    except (Error, pymongo.errors.OperationFailure, pymongo.errors.ServerSelectionTimeoutError) as err:

        print('{}'.format(err))


    print('users')
    for user in users.find():
        a_user = User(**user)
        print('User: {}'.format(a_user))
        print('User: {}'.format(repr(a_user)))

print('done')