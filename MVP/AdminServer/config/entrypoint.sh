#!/bin/bash 

a2ensite webApp.conf
apache2ctl -D FOREGROUND
    ## links the apache2 execution with the shell
    ## important in order to link the container life to the run of apache 