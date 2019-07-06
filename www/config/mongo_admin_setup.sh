#!/usr/bin/bash

# creates the initial mongodb users

echo "mongo admin setup called"

export ADMIN_PASSWORD='changeme'
export ROOT_PASSWORD='changeme'
export STARBUG_PASSWORD='changeme'


mongo admin --eval "db.createUser({ user: 'admin', pwd: '$ADMIN_PASSWORD', roles: [ { role: 'userAdminAnyDatabase', db: 'admin' }, 'readWriteAnyDatabase' ] });"

mongo admin -u admin -p $ADMIN_PASSWORD --authenticationDatabase admin --eval "db.createUser({ user: 'root', pwd: '$ROOT_PASSWORD', roles: [ { role: 'root', db: 'admin' }, 'readWriteAnyDatabase' ] });"

mongo starbug -u admin -p $ADMIN_PASSWORD --authenticationDatabase admin --eval "db.createUser({ user: 'starbug', pwd: '$STARBUG_PASSWORD', roles: [ { role: 'readWrite', db: 'starbug' } ] });"

