# starbug mongodb

These are scripts for creating and maintaining the starbug monogo database.

obsui.py has the factory and main functions.


# Initial passwords

Dockerfile.mongodb will copy conf/mongo_admin_setup.sh to
/docker-entrypoint-initdb.d/.  This file will create the initial
mongodb users admin, root and starbug.  It also contains their initial
passwords as examples that should be changed before building. The
conf/obs-flask.cfg file uses the starbug account to access the
database, so the uri must also be updated to match. This is
hardcoded factory input in the gobsui.py for gunicorn to find it,
but it is a command line argument for obsui.main() and can
be set as needed for testing.


# Environment

Setup a virtual environment for python to run from the command line for development and testing.

```
[lrm@lrmz-iMac starbugdb (master)]$ virtualenv -p /usr/local/bin/python3 py3env
Running virtualenv with interpreter /usr/local/bin/python3
Using base prefix '/usr/local/Cellar/python3/3.6.4_2/Frameworks/Python.framework/Versions/3.6'
New python executable in /Users/lrm/src/starbug/starbugdb/py3env/bin/python3.6
Also creating executable in /Users/lrm/src/starbug/starbugdb/py3env/bin/python
Installing setuptools, pip, wheel...done.



[lrm@lrmz-iMac starbugdb (master)]$ virtualenv -p /usr/local/bin/python3 py3env
Running virtualenv with interpreter /usr/local/bin/python3
Using base prefix '/usr/local/Cellar/python3/3.6.4_2/Frameworks/Python.framework/Versions/3.6'
New python executable in /Users/lrm/src/starbug/starbugdb/py3env/bin/python3.6
Also creating executable in /Users/lrm/src/starbug/starbugdb/py3env/bin/python
Installing setuptools, pip, wheel...done.



[lrm@lrmz-iMac starbugdb (master)]$ source py3env/bin/activate
(py3env) [lrm@lrmz-iMac starbugdb (master)]$ pip install -r requirements.txt
Collecting bcrypt (from -r requirements.txt (line 3))
  Using cached bcrypt-3.1.4-cp36-cp36m-macosx_10_6_intel.whl
Collecting flask (from -r requirements.txt (line 4))
  Using cached Flask-0.12.2-py2.py3-none-any.whl
Collecting Flask-PyMongo (from -r requirements.txt (line 5))
  Using cached Flask_PyMongo-0.5.1-py3-none-any.whl
Collecting Flask-Login (from -r requirements.txt (line 6))
Collecting gunicorn (from -r requirements.txt (line 7))
  Using cached gunicorn-19.7.1-py2.py3-none-any.whl
Collecting six>=1.4.1 (from bcrypt->-r requirements.txt (line 3))
  Using cached six-1.11.0-py2.py3-none-any.whl
Collecting cffi>=1.1 (from bcrypt->-r requirements.txt (line 3))
  Using cached cffi-1.11.4-cp36-cp36m-macosx_10_6_intel.whl
Collecting Werkzeug>=0.7 (from flask->-r requirements.txt (line 4))
  Using cached Werkzeug-0.14.1-py2.py3-none-any.whl
Collecting Jinja2>=2.4 (from flask->-r requirements.txt (line 4))
  Using cached Jinja2-2.10-py2.py3-none-any.whl
Collecting click>=2.0 (from flask->-r requirements.txt (line 4))
  Using cached click-6.7-py2.py3-none-any.whl
Collecting itsdangerous>=0.21 (from flask->-r requirements.txt (line 4))
Collecting PyMongo>=2.5 (from Flask-PyMongo->-r requirements.txt (line 5))
  Using cached pymongo-3.6.0-cp36-cp36m-macosx_10_6_intel.whl
Collecting pycparser (from cffi>=1.1->bcrypt->-r requirements.txt (line 3))
Collecting MarkupSafe>=0.23 (from Jinja2>=2.4->flask->-r requirements.txt (line 4))
Installing collected packages: six, pycparser, cffi, bcrypt, Werkzeug, MarkupSafe, Jinja2, click, itsdangerous, flask, PyMongo, Flask-PyMongo, Flask-Login, gunicorn
Successfully installed Flask-Login-0.4.1 Flask-PyMongo-0.5.1 Jinja2-2.10 MarkupSafe-1.0 PyMongo-3.6.0 Werkzeug-0.14.1 bcrypt-3.1.4 cffi-1.11.4 click-6.7 flask-0.12.2 gunicorn-19.7.1 itsdangerous-0.24 pycparser-2.18 six-1.11.0

```




# mongodb


## database storage

One time setup. This will also be implicitly created from the command line.

```
docker volume create starbugdata
docker volume create starbugbackup
```

## build docker image

```
docker build -f Dockerfile.mongodb -t starbugdb .
```

## run mongodb

with persistant volumes starbugdata for data storage and starbugbackup for temporary backup storage.

```
docker run --net starbugnet --mount source=starbugdata,target=/data/db  --mount source=starbugbackup,target=/opt/starbug.com/backup --name starbugdb_00 -d -p 27017:27017 lrmcfarland/starbugdb
```




# Gunicorn UI


## build docker image

```
docker build -f Dockerfile.obsui -t obsui-gunicorn .
```

## run gunicorn

```
docker run --net starbugnet --name obsui-gunicorn_00 --mount source=aai-logs,target=/opt/starbug.com/logs/gunicorn -d -p 8090:8090 obsui-gunicorn
```

to open a bash to look the logs:

```
docker exec -it obsui-gunicorn bash
```

## obsui-gunicorn docker image

```
docker build -f Dockerfile.obsui -t obsui-gunicorn .
```


# Add users

TODO use flask-login instead

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
