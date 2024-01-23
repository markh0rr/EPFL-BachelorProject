from flask import Flask, request, send_file
import jwt, json
import db 
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_PASSWORD")

def extract_info_from_request(request_data):
    parsed = False
    project_id = -1
    server_id = ""
    signed_token = request_data.get("token", "")

    try :
        token_content = jwt.decode(signed_token, key=os.getenv("TOKEN_SIGNING_SECRET"), algorithms='HS256')
    
        if not "pid" in token_content.keys() :
            raise Exception("incomplete token")
        project_id = token_content["pid"]

        if not "sid" in request_data.keys() :
            raise Exception("no server id")
        server_id = request_data["sid"]

        parsed = True

    except Exception as e :
        print("token incomplete or not authentic")
    
    return (parsed, project_id, server_id)

@app.route("/get_tasks/", methods=["POST"])
def get_tasks():
    dbs = None
    try :
        parsed,project_id,server_id = extract_info_from_request(request.json)
        if not parsed : 
            raise Exception("invalid token")
        
        dbs = db.get_session() 
        
        ## check if the server does not exist in DB register it
        already_registered = False   
        with dbs.cursor() as dbc : 
            dbc.execute("SELECT sid FROM servers WHERE sid = %s AND project_id = %s;", (server_id, project_id))
            server_info = dbc.fetchone()
            if server_info :
                already_registered = True
        
        if not already_registered : 
            with dbs.cursor() as dbc : 
                dbc.execute("INSERT INTO servers(sid, project_id, join_date) VALUES(%s, %s, NOW());", (server_id, project_id))
                dbs.commit()
                raise Exception("no task when you just registered")

        ## if the server is already registered look for tasks 
        with dbs.cursor() as dbc : 
            dbc.execute("SELECT id, task_json FROM tasks WHERE project_id = %s AND server_id = %s AND completed = 0 ORDER BY id ASC;", (project_id, server_id))
            task = dbc.fetchone()
            if not task:
                raise Exception("no task")
            dbc.fetchall()
            dbs.close()

            task_json = {
                "task_id" : task[0],
                "task_json" : task[1]
            }
            answer = json.dumps(task_json)
            
            dbs.close()
            return answer

    except Exception as e :
        if dbs :
            dbs.close()
        return str(e)

@app.route("/fetch_script/", methods=["POST"])
def fetch_script():
    dbs = None
    try :
        parsed,project_id,server_id = extract_info_from_request(request.json)
        if not parsed : 
            raise Exception("invalid token")

        if 'file_id' not in request.json.keys():
            raise Exception("no script id in the post form")
        script_id =  request.json['file_id']

        dbs = db.get_session()
        with dbs.cursor() as dbc :
            dbc.execute("SELECT user_id FROM scripts_servers WHERE project_id = %s AND server_id = %s AND script_id = %s;", (project_id, server_id, script_id))
            user_id = dbc.fetchone()
            if not user_id :
                raise Exception("no such file share")

            script_path = f"/user_files/user_{user_id[0]}/scripts/script_{script_id}"
            if not os.path.exists(script_path):
                raise Exception("script not found in the file tree")
            
            dbs.close()
            return send_file(script_path)

    except Exception as e :
        if dbs :
            dbs.close()
        return ""

@app.route("/fetch_image/", methods=["POST"])
def fetch_image():
    dbs = None
    try :
        parsed,project_id,server_id = extract_info_from_request(request.json)
        if not parsed : 
            raise Exception("invalid token")

        if 'file_id' not in request.json.keys():
            raise Exception("no image id in the post form")
        image_id =  request.json['file_id']

        dbs = db.get_session()
        with dbs.cursor() as dbc :
            dbc.execute("SELECT user_id FROM images_servers WHERE project_id = %s AND server_id = %s AND image_id = %s;", (project_id, server_id, image_id))
            user_id = dbc.fetchone()
            if not user_id :
                raise Exception("no such file share")

            image_path = f"/user_files/user_{user_id[0]}/images/image_{image_id}"
            if not os.path.exists(image_path):
                raise Exception("image not found in the file tree")
            
            dbs.close()
            return send_file(image_path)

    except Exception as e :
        if dbs :
            dbs.close()
        return ""

@app.route("/post_task_feedback/", methods=["POST"])
def post_feedback():
    dbs = None
    try :
        parsed,project_id,server_id = extract_info_from_request(request.json)
        if not parsed : 
            raise Exception("invalid token")
        
        if "task_id" not in request.json.keys():
            raise Exception("no job provided")
        task_id = request.json["task_id"]

        dbs = db.get_session()
        with dbs.cursor() as dbc :
            dbc.execute("SELECT * FROM tasks WHERE id = %s AND project_id = %s AND server_id = %s;", (task_id, project_id, server_id))
            task = dbc.fetchone()
            if not task :
                raise Exception("no such task")
            
            dbc.execute("UPDATE tasks SET completed = 1 WHERE id = %s AND project_id = %s AND server_id = %s;", (task_id, project_id, server_id))
            dbs.commit()

            if "task_feedback" in request.json :
                task_feedback = request.json["task_feedback"]
                dbc.execute("INSERT INTO tasks_feedback(task_id, task_feedback, posted_at) VALUES(%s, %s, NOW());", (task_id, task_feedback))
                dbs.commit()

            dbs.close()
            return "successfully registered your feedback, thank you"
    except Exception as e :
        if dbs :
            dbs.close()
        return ""

@app.route("/post_server_feedback/", methods=["POST"])
def server_feedback():
    dbs = None
    try :
        parsed,project_id,server_id = extract_info_from_request(request.json)
        if not parsed : 
            raise Exception("invalid token")

        dbs = db.get_session()
        with dbs.cursor() as dbc :
            dbc.execute("SELECT * FROM servers WHERE project_id = %s AND sid = %s;", (project_id, server_id))
            task = dbc.fetchone()
            if not task :
                raise Exception("no such registered server")

            dbc.execute("SELECT * FROM servers_feedback WHERE project_id = %s AND server_id = %s;", (project_id, server_id))
            existing_feedback = dbc.fetchone()

            feedback = ""
            if "server_feedback" in request.json.keys() :
                feedback = request.json["server_feedback"]
            
            if existing_feedback :
                dbc.execute("UPDATE servers_feedback SET feedback = %s, posted_at = NOW() WHERE project_id = %s AND server_id = %s;", (feedback, project_id, server_id))
            else :
                dbc.execute("INSERT INTO servers_feedback(project_id, server_id, feedback, posted_at) VALUES(%s, %s, %s, NOW());", (project_id, server_id, feedback))
            dbs.commit()
            dbs.close()
            return "thanks for your ping/feedback, taken in account"
        
    except Exception as e :
        if dbs :
            dbs.close()
        return ""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5454, debug=True)