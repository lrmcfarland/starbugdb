// initialize starbugdb
//
// run on a blank database
// adds starbug users, but not admin
//
// TODO needs initial admin user added from a mongo shell first with very limitied role
//
// $ docker exec -it starbugdb-00 mongo admin
//
// > db.createUser({ user: 'admin', pwd: 'changeme', roles: [ { role: 'userAdminAnyDatabase', db: 'admin' } ] });
//
// then this script:     mongo admin add_users.js
//
// to test               mongo starbug insert_test_data.js
//                       mongo starbug authafterconn.js
//
// after auth:
// mongo shell admin:    mongo admin -u admin -p changeme --authenticationDatabase admin
// mongo shell starbug:  mongo starbug -u starbug -p changemetoo --authenticationDatabase starbug
//
// make backup (./dump): mongodump -u root -p changem3
//
//
// load user config JSON
// Assumes format is [{user:<user>, db:<db>, create_args: {user:<user>, pwd:<password>, roles: [{role: <role>, db:<db>}]}

var users = JSON.parse(cat("users.json")); // TODO from command line args

print(JSON.stringify(users, undefined, 2)); // TODO rm

var conn = new Mongo(); // Mongo(<host:port>)
var admindb = conn.getDB('admin');

try {
     // ASSUMES: admin user has already been created manually as above
    admindb.auth(users['admin']['create_args']['user'], users['admin']['create_args']['pwd']);
} catch (err) {
    print(err);
    throw new Error("auth user must be added from a mongo shell first");
}

// assumes admin is user[0] and already exists
for (var key in users) {

    print('add: ' + JSON.stringify(users[key], undefined, 2));

    try {
	userdb = conn.getDB(users[key]['db']);
	userdb.createUser(users[key]['create_args']);

    } catch (err) {
	print(err);
    }

}
