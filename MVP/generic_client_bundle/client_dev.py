#!/bin/python3

"""
Client script that periodically ask the server for tasks
the tasks can be of following types :
    - fetch a file (docker image, scripts, ...)
    - execute a script 
"""

import os, subprocess
import requests, json 
import random, string
import time 
import threading

DEBUG = False
headers = {"Content-type":"application/json"}

## parallel method to ping the server 
def ping_function(token, server_unique_id, full_api_address, DEBUG):
    data = {
        "token" : token, 
        "sid" : server_unique_id 
    }
    
    while True :
        ### data["server_feedback"] = "some feedback text"
            # it is possible to send feedback by setting the "server_feedback" key 
            # of the json data to some usefull text 
        if DEBUG :
            print("[+] pinging")

        try :
            answer = requests.post(f"{full_api_address}/post_server_feedback/", json=data, headers=headers)
            if DEBUG :
                print(f"    [*] {answer.text}")
        except Exception as e :
            if DEBUG :
                print(f"    [-] {str(e)}")
        time.sleep(30)

## the first time this scripts runs it creates a random unique id that is 
## with verify probability unique among server of a cluster (at most a 100 of servers)
server_unique_id = None 
if not os.path.exists("./server_unique_id"):
    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.octdigits
    server_unique_id = ''.join(random.choice(alphabet) for i in range(60))
    if DEBUG :
        print(f"[+] server unique random id created : {server_unique_id}")
    with open("server_unique_id", 'w') as f:
        f.write(server_unique_id)
else:
    with open("server_unique_id", 'r') as f :
        server_unique_id = f.read()

## load the token and the server address 
token = None 
with open("token", 'r') as f :
    token = f.read()

api_address = None 
with open("hostname", 'r') as f :
    api_address = f.read()

## start the service 
if server_unique_id != None and token != None and api_address != None : 
    full_api_address = f"http://{api_address}:9494"
    feedback_thread = threading.Thread(target=ping_function, args=(token, server_unique_id, full_api_address, DEBUG))
    feedback_thread.start()

    if DEBUG :
        print(full_api_address)
    while True :
        try :
            request_data = {
                'token':token,
                'sid':server_unique_id
            }

            ## fetch instruction 
            response = requests.post(f"{full_api_address}/get_tasks/", json=request_data, headers=headers)
            if not response.text :
                raise Exception("not a valid task")
            
            if DEBUG : 
                print(f"[+] fetched : {response.text}")
            
            ## parse instruction 
            task = json.loads(response.text)
            if type(task) != dict:
                raise Exception("not a valid answer")

            if "task_id" in task.keys() and "task_json" in task.keys() :
                ## parse the task content 
                task_id = task["task_id"]
                task_json = task["task_json"]
                task_content = json.loads(task_json)

                if DEBUG :
                    print(f"    [*] {task_id}")
                    print(f"    [*] {task_json}")

                if type(task_content) != dict:
                    raise Exception("not a valid task description")

                if not "file_id" in task_content.keys() or not "file_name" in task_content.keys() or not "task_type" in task_content.keys():
                    raise Exception("invalid task content")
                
                if DEBUG :
                    print(f"    [*] {task_content['file_name']}")
                    print(f"    [*] {task_content['file_id']}")
                    print(f"    [*] {task_content['task_type']}")

                ## download the file associated with the task
                if not os.path.exists("./downloads"):
                    os.mkdir("./downloads")

                fetch_from_url = ""
                if task_content["task_type"] == "download_image" :
                    fetch_from_url = "fetch_image/"
                elif task_content["task_type"] == "execute_script":
                    fetch_from_url = "fetch_script/"

                if DEBUG :
                    print(f"    [*] request data : {request_data}")
                    print(f"    [*] request url : {full_api_address}/{fetch_from_url}")
                
                request_data["file_id"] = task_content["file_id"]
                answer = requests.post(f"{full_api_address}/{fetch_from_url}", json=request_data, headers=headers)

                filename = task_content['file_name']
                if answer.status_code >= 200 and answer.status_code < 300 and answer.content : 
                    with open(f"./downloads/{filename}", 'wb') as f:
                        f.write(answer.content)
                else :
                    raise Exception("invalid file response")
                
                ## in case the task is run script, run the downloaded script 
                if task_content["task_type"] == "execute_script" : 
                    ##  run the script
                    capture_output = task_content["capture_output"]
                    p = subprocess.run(["bash", f"./downloads/{filename}"], capture_output=capture_output, text=True, timeout=300)                     

                    if capture_output : 
                        task_feedback = {
                            "stderr_feedback" : p.stderr,
                            "stdout_feedback" : p.stdout
                        }
                        task_feedback_json = json.dumps(task_feedback)
                        request_data["task_feedback"] = task_feedback_json

                ## send feedback to the server
                request_data["task_id"] = task["task_id"]
                answer = requests.post(f"{full_api_address}/post_task_feedback/", json=request_data, headers=headers)
                
                if DEBUG :
                    print(f" [+] succeeded with the task")
                    print(f" [*] {answer.text}")
            else :
                raise Exception("invalid arguments")

        except Exception as e :
            if DEBUG :
                print(f"    [-] {str(e)}")
        time.sleep(3)