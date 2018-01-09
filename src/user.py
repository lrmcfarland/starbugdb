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

    def __init__(self, _id=0, email=None, password=None, authenticated=True, active=True, anon=False, write=False):

        """Matches records in starbug.users table.

        _id is intended for mongo's generated id

        > db.users.insert({"email": "lrm@starbug.com", "password": "changeme", "authenticated":false, "active":false, "anon":false})


        Args
            _id (unicode): unicode id, used by the login manager too
            email (str):   user's email as username
            password (str): user's password

            authenticated (bool): an authentication state
            active (bool):  an active state
            anon (bool): an anonymous state
            write (bool): extra check for insert TODO use mongo roles?
        """

        self._id = _id
        self.email = email
        self.password = password
        self.authenticated = authenticated
        self.active = active
        self.anon = anon
        self.write = write

        return


    def __str__(self):
        return '({_id}, {email}, ********, {authenticated}, {active}, {anon}, {write})'.format(**self.__dict__)


    def __repr__(self):
        return r'{{ {email}, "password": {password}, "authenticated":{authenticated}, "active":{active}, "anon":{anon}, "write":{write} }}'.format(**self.__dict__)


    def get_id(self):
        """for the flask login manager"""
        return unicode(self._id)


    def for_insert(self):
        """Returns a dictionary for mongodb insert, i.e. no _id"""
        return {'email': self.email,
                'password': self.password,
                'authenticated': self.authenticated,
                'active': self.active,
                'anon': self.anon,
                'write': self.write}


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

    parser.add_argument('-u', '--email', type=str, dest='email', required=True,
                        metavar='email', help='user email')

    parser.add_argument('-p', '--password', type=str, dest='password', required=True,
                        metavar='password', help='user password')

    parser.add_argument('-w', '--write', action='store_true',
                        dest='write', default=defaults['can write'],
                        help='user has write privileges (default: %(default)s)')

    args = parser.parse_args()

    # TODO rm user, deactiveate, anon?

    # ----- add user -----

    try:

        client = pymongo.MongoClient(args.host, args.port)

        client.admin.authenticate(args.admin_name, args.admin_password)

        users = client['starbug']['users']

        # check user doesn't already exist, TODO mongo to enforce unique index on name?

        found = users.find_one({'email': args.email}) # gets the first one
        if found:
            a_user = User(**found)
            raise Error('user {} already exists'.format(a_user))

        a_user = User(email=args.email,
                      password = bcrypt.hashpw(args.password.encode('utf-8'), bcrypt.gensalt()),
                      write=args.write)

        users.insert(a_user.for_insert())

    except (Error, pymongo.errors.OperationFailure, pymongo.errors.ServerSelectionTimeoutError) as err:

        print('{}'.format(err))


    print('users')
    for user in users.find():
        a_user = User(**user)
        print('User: {}'.format(a_user))
        print('User: {}'.format(repr(a_user)))

print('done')
