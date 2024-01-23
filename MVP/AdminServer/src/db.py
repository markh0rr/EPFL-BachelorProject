import mysql.connector as db_connector
import os

db_config = {
    'username' : os.getenv("DB_USER"),
    'password' : os.getenv("DB_PASSWORD"),
    'host' : os.getenv("DB_HOSTNAME"),      ## name of the docker db image, as it stands in a docker private bridge network
                                ## it can be referenced by container_name instead of IP 
    'database' : os.getenv("DB_NAME")
}

def get_session():
    db_session = None
    try :
        db_session = db_connector.connect(**db_config)
    except Exception as e :
        print("failed to connect to the kapitan DB")
        print(str(e))
    return db_session