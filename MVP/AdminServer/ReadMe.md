# The Admin server 

The Admin server of the project. Provides user with a web UI dashboard to register deployment 
projects, upload scripts, configure and manage deployement infrastructure remotely. 

The one place for all your deployement projects. 

The Admin server is using the flask framework together with python to serve http requests. 

As the flask  built-in development server development isn't recommanded for production. The production container wraps the flask admin service with an apache server. 

## Build, Run & Use 

All docker commands bellow have to be executed within the working directory of this ReadMe.md file, except for the docker-compose file.  

### How to build

For developpment, the built-in flask server suffies :
```
docker build -f Dockerfile.flask -t dev_kapitan_admin_server .
```

For deployement it is preferable to have an apache server : 
```
docker build -f Dockerfile.apache -t kapitan_admin_server .
```

### How to run 

The docker compose file at `/MVP` enables to spin up the whole software system.

In order to only run the admin server development image manually, after the build, execute the following command :
```
docker run \
    -p 7474:5454 \
    -it -d --rm \
    -v ./src:/webApp/ \
    dev_kapitan_admin_server
```

In order to only run the apache admin server image manually, after the build, create certificates on the host with openssl : 
```
openssl req -x509 \
            -days ndays \
            -nodes \
            -newkey rsa:2048 -keyout server.key \
            -sha256 -out server.crt 
```

with : 
- `req`, starts the openssl tool req for creating and processing certificates 
- `-x509`, flag to self sign the certificate 
- `-days ndays`, lifetime of the certificate 
- `-nodes`, enables to access the private.key without a password locally for conveniance of use by applications, like apache
- `-newkey rsa:2048 -key server.key`, output a rsa of 2048 bits private key 
- `-sha256`, use of sha256 algorithm to hash the certificate data and sign the certificate
- `-out server.crt`, outputs the certificate 

Then execute the image with the certificate folder mounted : 
```
docker run \
    -it \
    -p 7474:5454 \
    -v /host_certificate_folder:/server_ssl \
    -e FLASK_SECRET_KEY=set_a_random_of_64_characters_here \
    kapitan_admin_server
```

### How to access 

The admin webpage is available at `localhost:7474` as the container bridge network is set to forward the service port to the host with the -p flag.
