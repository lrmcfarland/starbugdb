// Example mongo script for auth after connection using Mongo()
// https://docs.mongodb.com/manual/tutorial/write-scripts-for-the-mongo-shell/
//
// configure as per readme with auth and starbug users, but with starbug in the starbug database
//
// to run: mongo authafterconn.js
//


var conn = new Mongo(); // Mongo(<host:port>)
var starbugdb = conn.getDB("starbug");

var users = JSON.parse(cat("../conf/users.json"));
starbugdb.auth(users['starbug']['create_args']['user'], users['starbug']['create_args']['pwd']);

var cursor = starbugdb.observations.find();

while ( cursor.hasNext() ) {
    printjson( cursor.next() );
}
