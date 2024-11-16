db = db.getSiblingDB(process.env.MONGO_DBNAME); // Switch to 'dockership' database

db.createUser({
    user: process.env.MONGO_USERNAME,
    pwd: process.env.MONGO_PASSWORD,
    roles: [
        { role: "readWrite", db: process.env.MONGO_DBNAME }
    ]
});
