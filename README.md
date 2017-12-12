# starbug mongodb

These are scripts for creating and maintaining the starbug monogo database.

# build

One time setup

```
docker volume create starbug-data
```

build image

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
mongodump -u root -p changem3 [--out <path>]

mongodump -u root -p changem3

[rmcfarland@VSN00249 starbug.com (starbugdb-v2)]$ mongodump -u root -p changem3 [--out <path>]


2017-12-08T13:59:19.137-0800	writing admin.system.users to
2017-12-08T13:59:19.139-0800	done dumping admin.system.users (3 documents)
2017-12-08T13:59:19.139-0800	writing admin.system.version to
2017-12-08T13:59:19.140-0800	done dumping admin.system.version (2 documents)
2017-12-08T13:59:19.140-0800	writing starbug.observations to
2017-12-08T13:59:19.142-0800	done dumping starbug.observations (6 documents)

```

Dumps in ./dump by default with out --out arg


# Restore


```
$ mongorestore -u root -p changem3 [--drop <path>]

2017-12-08T14:07:11.390-0800	using default 'dump' directory
2017-12-08T14:07:11.390-0800	preparing collections to restore from
2017-12-08T14:07:11.393-0800	reading metadata for starbug.observations from dump/starbug/observations.metadata.json
2017-12-08T14:07:11.532-0800	restoring starbug.observations from dump/starbug/observations.bson
2017-12-08T14:07:11.535-0800	no indexes to restore
2017-12-08T14:07:11.535-0800	finished restoring starbug.observations (6 documents)
2017-12-08T14:07:11.535-0800	restoring users from dump/admin/system.users.bson
2017-12-08T14:07:11.699-0800	done

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
