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
$ mongo admin add_users.js
```

# Test




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
