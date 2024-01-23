# The DBMS

The data base management system is a central service of the project. It does the bridge between 
the admin and the clients, by storing configurations, projects, scripts to be executed by the 
client server. 

The required DBMS type for this project is relationnal. Therefore the project uses a containerized version of mysql. 

## A custom DBMS image

The database image is based on the mysql image provided on docker hub. 

The DBMS container, has to mount a host volume to it's data `/mysql` folder for persistance of the data, as container are stateless.  

When dockerized mysql scripts instantiates, they run mysql scripts from `/docker-entrypoint-initdb.d/`.

By placing a configuration script in this volume, we conditionnaly create the database, tables and users at the first run of the image. Since database modifications impacts the DMBS data folder, latter run of the mysql instante will load the database configuration from the `mysql` folder, and the script will not be executed.

## Build, Run & Use 

### Build

Run the following command within the workdir of this ReadMe.md file, to build the dbms image : 
```
docker build -t kapitan_db .
```

### Run 

The docker compose file at `/MVP` enables to spin up the whole software system

In order to only start the dbms container, run the following command (workdir independant) and provide a password :
```
docker run \
    -d \
    -e MYSQL_ROOT_PASSWORD=provide_a_password \
    --restart unless-stopped \
    -p 3306:3306 \
    -v hostVolume:/var/lib/mysql \
    kapitan_db
```

The password is used to configure mysql on it's first run. 

### Access the DBMS

The DBMS can be accessed from the host with the password provided in the previous commands :
```
mysql -u root -p --protocol=tcp
```

## DataBase Structure 

The DBMS is configured to host one database, nammed `kapitan_db`.

The database has the following tables : 
- `users`, admin accounts
- `projects`, user created projects, ownership is set by the use of foreign key 
- `servers`, servers are registered server clients and associated with at least one project
- `feedback`, the periodic feedback send by the servers is stored here

