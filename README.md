# starbug mongodb

These are scripts for creating and maintaining the starbug monogo database.

# TODO

gunicorn is hit and miss with this authentication (using mognodb's
user accounts as described below). after login intermittently
complains that "no user is authenticated", but will sometimes work
when re-clicked. session problem? running the flask ui directly is ok
with it.

# conf

create conf/users.json and conf/aai-flask.cfg with database configuration
and user credentials. These are not in .gitignore to provide an examle
and for testing, but do need to be changed before production.

TODO add a test that they are.


## conf/users.json

mongodb users example

```
{
  "admin": {
    "db": "admin",
    "comment": "assumed to have been added manually in the mongo shell before the others",
    "create_args": {
      "user": "admin",
      "pwd": "changeme",
      "roles": [
	{
	  "role": "userAdminAnyDatabase",
	  "db": "admin"
	}
      ]
    }
  },
  "root": {
    "db": "admin",
    "create_args": {
      "user": "root",
      "pwd": "changemetoo",
      "roles": [
	{
	  "role": "root",
	  "db": "admin"
	}
      ]
    }
  },
  "starbug": {
    "db": "starbug",
    "create_args": {
      "user": "starbug",
      "pwd": "changeme3",
      "roles": [
	{
	  "role": "dbAdmin",
	  "db": "starbug"
	},
	{
	  "role": "readWrite",
	  "db": "starbug"
	}
      ]
    }
  },
  "guest": {
    "db": "starbug",
    "create_args": {
      "user": "guest",
      "pwd": "guest",
      "roles": [
	{
	  "role": "read",
	  "db": "starbug"
	}
      ]
    }
  }
}

```

## conf/aai-flask.cfg

aai-flask.cfg example. This needs the starbug credentials created above.

```
# base line aai flask config
# https://flask-pymongo.readthedocs.io/en/latest/

SECRET_KEY = 'seti2020'

# inside container 'mongodb://starbugdb-00/starbug'
MONGO_URI = 'mongodb://localhost:27017/starbug'

MONGO_DBNAME = 'starbug'

```


# build

## database storage

One time setup

```
docker volume create starbug-data
```

## build docker image

```
docker build -f Dockerfile.mongodb -t starbugdb .

```

# run

```
docker run --net starbugnet --mount source=starbug-data,target=/data/db --name starbugdb-00 -d -p 27017:27017 starbugdb --auth
```

# Initialize database

I am still working on how to fully automate this, but for now, I am
having authorization issues when I try to generate the admin:
userAdminAnyDatabase in a script. The work around is to create this one
by hand:

```
$ docker exec -it starbugdb-00 mongo admin

 > db.createUser({ user: 'admin', pwd: 'changeme', roles: [ { role: 'userAdminAnyDatabase', db: 'admin' } ] });

```

The add users script creates root (for dump and restore), starbug (for dbAdmin, read/write), and guest (for read)

```
$ cd src
$ mongo admin add_users.js
```

[To chage a password](https://docs.mongodb.com/v3.0/reference/method/db.changeUserPassword/)


# Test

```
$ cd src

$ mongo insert_test_data.js

$ mongo starbug authafterconn.js
MongoDB shell version v3.4.10
connecting to: mongodb://127.0.0.1:27017/starbug
MongoDB server version: 3.4.10
{
	"_id" : ObjectId("5a29c8d24aeaaa7bc3662be4"),
	"name" : "Mercury",
	"type" : "planet",
	"datetime" : "2017-12-06T05:00:00-8"
}
{
	"_id" : ObjectId("5a29c8d34aeaaa7bc3662be5"),
	"name" : "Venus",
	"type" : "planet",
	"datetime" : "2017-12-06T06:00:00-8"
}

```

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
