# starbug observation database

These are scripts for creating and maintaining the starbug observations database.
This consists of two containers: an observation database and a web ui to it.

The first part is simply a mongodb server running in a container.


# Build

## mongo database

The database image is build from
[Dockerfile.mongodb](https://github.com/lrmcfarland/starbugdb/blob/master/Dockerfile.mongodb).

```
docker build -f Dockerfile.mongodb -t starbugdb .
```

Mongodb configuration is read at run time from
[config/mongo_admin_setup.sh](https://github.com/lrmcfarland/starbugdb/blob/master/www/config/mongo_admin_setup.sh)
This will initialize the admin, root and starbug accounts with their
passwords as "changeme".

TODO create change_password.py


## Observation UI

The web UI image is built from
[Dockerfile.obsui](https://github.com/lrmcfarland/starbugdb/blob/master/Dockerfile.obsui).

```
docker build -f Dockerfile.obsui -t obsui .
```

# Deploy

## docker compose


```
docker-compose -f stdb-compose.yaml up -d

docker-compose -f stdb-compose.yaml ps

docker-compose -f stdb-compose.yaml down

```


## docker cli


To deploy with out docker compose

### starbug database

```
docker run --net starbugnet --mount source=starbugdata,target=/data/db  --mount source=starbugbackup,target=/opt/starbug.com/backup --name starbugdb_00 -d -p 27017:27017 lrmcfarland/starbugdb
```

This will create the starbugdata and starbugbackup volumes

```
docker volume create starbugdata
docker volume create starbugbackup
```

### Observations UI

```
docker run --net starbugnet --name obsui-gunicorn_00 --mount source=aai-logs,target=/opt/starbug.com/logs/gunicorn -d -p 8090:8090 obsui-gunicorn
```

# logging

To open a bash shell to look the logs:

```
docker exec -it obsui-gunicorn bash

cd /opt/starbug.com/logs

```


# Runtime Environment

with pyenv

```
$ pyenv virtualenv 3.6.4 obsdb-3.6.4

$ pyenv activate obsdb-3.6.4

$ pip install -r requirements.txt

```


# Passwords

## database access

Dockerfile.mongodb will copy
[conf/mongo_admin_setup.sh](https://github.com/lrmcfarland/starbugdb/blob/master/www/conf/mongo_admin_setup.sh)
to /docker-entrypoint-initdb.d/.  This file will create the initial
mongodb users admin, root and starbug. It also contains their initial
passwords as examples that should be changed when deployed to production, e.g. on persistent storage.

The
[conf/obsui_starbug.cfg](https://github.com/lrmcfarland/starbugdb/blob/master/www/conf/obsui_starbug.cfg)
file contains the web server configuation information and should also changed when deployed to production.
This must match the hard coded factory input in the
[gobsui.py](https://github.com/lrmcfarland/starbugdb/blob/master/www/gobsui.py)
for gunicorn to find it by default, but it is a command line argument
for obsui.main() and can be set as needed for testing.

## Observation UI access

The observation UI access is separate from the database access.
At this time you will need to use (user.py)[https://github.com/lrmcfarland/starbugdb/blob/master/www/user.py]
to add users on the host.
Until this is done, all user login attempts will fail as 'no user <user>'.

Using the default admin name and admin password from above, this will add the user guest

```

$ ./user.py -u guest -p guest

```
If it has not already been done, this will create the starbug database on the local mongodb.
Users passwords are stored hashed with bcrypt. The src/add_user.py
script will install them.  At this time this is the only way to add
users.

There is no web UI to do this at this time.

[To chage a password](https://docs.mongodb.com/v3.0/reference/method/db.changeUserPassword/)

# mongo access

Install the mongo client on the local host, e.g. brew instal mongodb

```
$ mongo admin -u admin -p changeme --authenticationDatabase admin
MongoDB shell version v4.0.3

> show dbs;
admin    0.000GB
config   0.000GB
local    0.000GB
starbug  0.000GB

> use starbug
switched to db starbug

> show tables;
users

> db.users.find()
{ "_id" : ObjectId("5cf94d46962e154802a331ec"), "username" : "guest", "password" : BinData(0,"JDJiJDEyJHAza1I4dFgvbjh1OXMzaUpPLmZhdk8uS1M4QlBVYzVmcGFMcU1najlmL2d3ZmFSdjhhLzND"), "authenticated" : true, "active" : true, "anon" : false }

> db.users.remove({'username':'guest'})
WriteResult({ "nRemoved" : 1 })


```


# Backup


## create a dump

```

$ docker run --rm --net starbugnet --mount source=starbugdata,target=/data/db --mount source=starbugbackup,target=/opt/starbug.com/backup mongo bash -c 'mongodump --out /opt/starbug.com/backup/starbugdbdump --host starbugdb_00:27017'
2018-08-01T06:00:15.465+0000	writing admin.system.users to
2018-08-01T06:00:15.466+0000	done dumping admin.system.users (3 documents)
2018-08-01T06:00:15.466+0000	writing admin.system.version to
2018-08-01T06:00:15.467+0000	done dumping admin.system.version (2 documents)
2018-08-01T06:00:15.467+0000	writing starbug.observations to
2018-08-01T06:00:15.467+0000	writing starbug.users to
2018-08-01T06:00:15.468+0000	done dumping starbug.observations (43 documents)
2018-08-01T06:00:15.469+0000	done dumping starbug.users (2 documents)
```


### create a tar ball in container

```
$ docker exec -it starbugdb_00 bash

# cd /opt/starbug.com/backup/

# tar cvzf starbugdbdump.tgz starbugdbdump

```


### copy tar ball to VM

```
$ docker cp starbugdb_00:/opt/starbug.com/backup/starbugdbdump.tgz ./

```


# Restore

Start mongo with out auth to load dump for the first time on an empty database

```
$ docker run --net starbugnet --mount source=starbug-data,target=/data/db --name starbugdb_00 -d -p 27017:27017 starbugdb

$ mongorestore --drop dump
2017-12-27T20:18:33.221-0800	preparing collections to restore from
2017-12-27T20:18:33.226-0800	reading metadata for starbug.observations from dump/starbug/observations.metadata.json
2017-12-27T20:18:33.238-0800	restoring starbug.observations from dump/starbug/observations.bson
2017-12-27T20:18:33.240-0800	no indexes to restore
2017-12-27T20:18:33.240-0800	finished restoring starbug.observations (7 documents)
2017-12-27T20:18:33.242-0800	restoring users from dump/admin/system.users.bson
2017-12-27T20:18:33.286-0800	done

```

But the database is open:

```

$ docker exec -it starbugdb_00 mongo admin
MongoDB shell version v3.6.0
connecting to: mongodb://127.0.0.1:27017/admin

> use starbug;
switched to db starbug
> show tables;
observations
> db.observations.find();
{ "_id" : ObjectId("5a4469d8b682b62844125b56"), "target_name" : "Saturn", "dst" : "false", "longitude" : "-122.08221056627683", "datetime" : ISODate("2017-11-28T18:05:00Z"), "date" : "2017-12-27", "ra" : "14:31:18.2", "time" : "22:05:00", "latitude" : "37.400154468444086", "timezone" : "-0700", "dec" : "-11:54:56", "notes" : "First light Celestron NexStar 8SE" }
{ "_id" : ObjectId("5a446a50b682b62844125b57"), "target_name" : "Saturn", "dst" : "false", "longitude" : "-122.08221056627683", "datetime" : ISODate("2013-04-12T19:09:00Z"), "date" : "2013-05-11", "ra" : "14:29:35.0", "time" : "23:09:00", "latitude" : "37.400154468444086", "timezone" : "-0700", "dec" : "-11:43:15.5", "notes" : "" }

```

Clear the image and restart with auth

```
$ docker run --net starbugnet --mount source=starbug-data,target=/data/db --name starbugdb_00 -d -p 27017:27017 starbugdb --auth


$ docker exec -it starbugdb_00 mongo admin
> use starbug;
switched to db starbug
> show tables;
2017-12-28T04:21:48.562+0000 E QUERY    [thread1] Error: listCollections failed: {
	"ok" : 0,
	"errmsg" : "not authorized on starbug to execute command { listCollections: 1.0, filter: {}, $db: \"starbug\" }",
	"code" : 13,
	"codeName" : "Unauthorized"
} :


$ mongo starbug -u starbug -p changeme3 --authenticationDatabase starbug
MongoDB shell version v3.6.0
connecting to: mongodb://127.0.0.1:27017/starbug
MongoDB server version: 3.6.0
> show tables;
observations
> db.observations.find();
{ "_id" : ObjectId("5a4469d8b682b62844125b56"), "target_name" : "Saturn", "dst" : "false", "longitude" : "-122.08221056627683", "datetime" : ISODate("2017-11-28T18:05:00Z"), "date" : "2017-12-27", "ra" : "14:31:18.2", "time" : "22:05:00", "latitude" : "37.400154468444086", "timezone" : "-0700", "dec" : "-11:54:56", "notes" : "First light Celestron NexStar 8SE" }
{ "_id" : ObjectId("5a446a50b682b62844125b57"), "target_name" : "Saturn", "dst" : "false", "longitude" : "-122.08221056627683", "datetime" : ISODate("2013-04-12T19:09:00Z"), "date" : "2013-05-11", "ra" : "14:29:35.0", "time" : "23:09:00", "latitude" : "37.400154468444086", "timezone" : "-0700", "dec" : "-11:43:15.5", "notes" : "" }


```




# Commands


```
> show users;
> show roles;


> db.dropUser('starbug');

> db.createUser({ user: 'starbug', pwd: 'changeme', roles: [ { role: 'dbAdmin', db: 'starbug' },  { role: 'readWrite', db: 'starbug' }] });


> use starbug;
switched to db starbug

> db.observations.insert({"name":"Jupiter", "moons": 4});
> db.observations.insert({"name":"Saturn", "rings": 16});
> db.observations.insert({"name”:”Mercury”});

> db.observations.find();
{ "_id" : ObjectId("5a2830c573af488ea1c56dfa"), "name" : "Jupiter", "moons" : 4 }
{ "_id" : ObjectId("5a2830eb73af488ea1c56dfb"), "name" : "Saturn", "rings" : 16 }

```



# to clean up

```
$ docker stop starbugdb_00
starbugdb_00

$ docker rm starbugdb_00
starbugdb_00

$ docker volume prune
WARNING! This will remove all volumes not used by at least one container.
Are you sure you want to continue? [y/N] y
Deleted Volumes:
starbug-data
04147de1d9fca5644d1173b95e350cb639c8cbea43985cf16171e01a30eadeb0

Total reclaimed space: 315.9MB

$ docker volume create starbug-data
starbug-data


```


# Test

TODO
