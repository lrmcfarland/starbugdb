// Example mongo script for auth before connection
//
// configure as per readme with auth and starbug users, but with starbug in the admin database
//
// to run  mongo starbug -u starbug -p changemetoo --authenticationDatabase starbug authbeforeconn.js
//


print("hello world");

function print_result(result) {
    print(tojson(result));
}

db.observations.find().forEach(print_result);
