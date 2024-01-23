# The API server

The API interface provided to clients to post feedback, fetch tasks, configurations and docker images. 

The API server is using the flask framework together with python to serve http requests. 

As the flask  built-in development server development is not recommanded for production. The production container wraps the flask api service with an apache server. 

## Build, Run & Use  

All docker commands bellow have to be executed within the working directory of this ReadMe.md file, except for the docker-compose file.  

### How to build

For development purposes, the built-in flask server suffies :
```
docker build -f Dockerfile.flask -t dev_kapitan_api_server .
```

For deployment purposes, the flask documentation recommands to associate flask with an apache server : 
```
docker build -f Dockerfile.apache -t kapitan_api_server .
```

### How to run 

The docker compose file at `/MVP` enables to spin up the whole software system

In order to only run the api server development image manually, after the build, execute the following command  :
```
docker run \
    -p 9494:5454 \
    -it -d --rm \
    -v ./src:/webApp/ \
    dev_kapitan_api_server
```

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
    -it -d --rm \
    -p 9494:5454 \
    -v /host_certificate_folder:/server_ssl \
    -e FLASK_SECRET_KEY=set_a_random_of_64_characters_here \
    kapitan_api_server
```

### How to Access  

The admin webpage is available at `localhost:9494` as the container bridge network is set to forward the service port to the host with the -p flag.