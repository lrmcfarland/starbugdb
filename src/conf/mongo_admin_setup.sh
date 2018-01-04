#!/usr/bin/bash

# creates the initial mongodb users

echo "mongo admin setup called"

export ADMIN_PASSWORD='changeme'
export ROOT_PASSWORD='changemetoo'
export STARBUG_PASSWORD='changeme3'


mongo admin --eval "db.createUser({ user: 'admin', pwd: '$ADMIN_PASSWORD', roles: [ { role: 'userAdminAnyDatabase', db: 'admin' } ] });"

mongo admin -u admin -p $ADMIN_PASSWORD --authenticationDatabase admin --eval "db.createUser({ user: 'root', pwd: '$ROOT_PASSWORD', roles: [ { role: 'root', db: 'admin' } ] });"

mongo starbug -u admin -p $ADMIN_PASSWORD --authenticationDatabase admin --eval "db.createUser({ user: 'starbug', pwd: '$STARBUG_PASSWORD', roles: [ { role: 'readWrite', db: 'starbug' } ] });"

