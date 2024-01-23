# The client bundle

## Presentation  

A script that fetches instructions from the admin server, and enables to 
- download files from the admin server (docker images, configuration files)
- execute shell scripts 

## Use 

Register this python script as a background service for linux, with sudo permissions. It requires python3 to be installed on the host. 

Step 1 : Unzip the client bundle in the `/etc/` directory as a folder with the name `client_bundle`

Step 2 : Copy the `kapitan_client.service` file to the `/etc/systemd/system` folder of the client machine 

Step 3 : 
```
sudo systemctl daemon-reload
sudo systemctl start kapitan_client
```

Step 4, enable the service to awake at boot : 
```
sudo systemctl enable kapitan_client
```

Step 5, check the status of the service with : 
```
sudo systemctl status kapitan_client
```