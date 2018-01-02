# starbug mongodb

These are scripts for creating and maintaining the starbug monogo database.



# pre build configure

Dockerfile.mongodb will copy conf/mongo_admin_setup.sh to
/docker-entrypoint-initdb.d/.  This file will create the initial
mongodb users admin, root and starbug.  It also contains their initial
passwords as examples that should be changed before building. The
conf/obs-flask.cfg file uses the starbug account to access the
database, so the uri must also be updated to match. I am still looking
for a better way to do this.

To run flask from a shell on the local host not inside docker (to
debug), you will need change the url as indicated in the comments.


# build

## database storage

One time setup

```
docker volume create starbug-data
```

## starbugdb docker image

```
docker build -f Dockerfile.obsui -t obsui-gunicorn .
```

### run

```
docker run --net starbugnet --name obsui-gunicorn-00 --mount source=aai-logs,target=/opt/starbug.com/logs/gunicorn -d -p 8090:8090 obsui-gunicorn
```

to open a bash to look the logs:

```
docker run -it --rm --mount source=aai-logs,target=/opt/starbug.com/logs/gunicorn --user root --entrypoint /bin/bash obsui-gunicorn
```

## obsui-gunicorn docker image

```
docker build -f Dockerfile.obsui -t obsui-gunicorn .
```

### run

```
docker run --net starbugnet --name obsui-gunicorn-00 --mount source=aai-logs,target=/opt/starbug.com/logs/gunicorn -d -p 8090:8090 obsui-gunicorn
```

to open a bash to look the logs:

```
docker run -it --rm --mount source=aai-logs,target=/opt/starbug.com/logs/gunicorn --user root --entrypoint /bin/bash obsui-gunicorn
```



# Add users

Users passwords are stored hashed with bcrypt. The src/add_user.py
script will install them.  At this time this is the only way to add
users. TODO use flask-login tool

```
$ cd src

$ ./add_user.py -u guest -p guest

$ ./add_user.py -u lister -p changeme -w


```

[To chage a password](https://docs.mongodb.com/v3.0/reference/method/db.changeUserPassword/)


# Test

todo

# Dump

Needs to be done as root

```
$ mongodump -u starbug -p changeme3 --authenticationDatabase starbug --out starbugdb_dump
2017-12-27T20:10:49.949-0800	positional arguments not allowed: [starbug]
2017-12-27T20:10:49.949-0800	try 'mongodump --help' for more information
(pyenv) [lrm@lrmz-iMac starbugdb (adds-flask-v4)]$ mongodump -u root -p changemetoo --authenticationDatabase admin --out dump
2017-12-27T20:11:01.829-0800	writing admin.system.users to
2017-12-27T20:11:01.836-0800	done dumping admin.system.users (4 documents)
2017-12-27T20:11:01.836-0800	writing admin.system.version to
2017-12-27T20:11:01.842-0800	done dumping admin.system.version (2 documents)
2017-12-27T20:11:01.842-0800	writing starbug.observations to
2017-12-27T20:11:01.849-0800	done dumping starbug.observations (7 documents)

```

Dumps in ./dump by default with out --out arg


# Restore

Start mongo with out auth to load dump for the first time on an empty database

```
$ docker run --net starbugnet --mount source=starbug-data,target=/data/db --name starbugdb-00 -d -p 27017:27017 starbugdb

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

$ docker exec -it starbugdb-00 mongo admin
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
$ docker run --net starbugnet --mount source=starbug-data,target=/data/db --name starbugdb-00 -d -p 27017:27017 starbugdb --auth


$ docker exec -it starbugdb-00 mongo admin
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
$ docker stop starbugdb-00
starbugdb-00

$ docker rm starbugdb-00
starbugdb-00

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
