from flask import Flask, render_template, session, request, redirect, url_for
from flask import flash, send_file
import constantes
import db
from datetime import datetime 
import os, shutil
import jwt, json, hashlib, random, string

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_PASSWORD")

def data_4_jinja():
    data = {}
    is_logged_in = session.get(constantes.s_IS_LOGGED_IN, default=False)
    data[constantes.s_IS_LOGGED_IN] = is_logged_in
    return data 

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("home"))

@app.route("/")
@app.route("/home/")
def home():
    """
    page functionnality
    """
    return render_template("index.html", data=data_4_jinja())

@app.route("/login/", methods=["GET", "POST"])
def login():
    """
    Login verification
    """
    is_logged_in = session.get(constantes.s_IS_LOGGED_IN, default=None)
    if is_logged_in :
        return redirect(url_for('home'))
    
    """
    Get request 
    """
    if request.method == "GET" :
        return render_template("pages/login.html", data=data_4_jinja())

    """
    Post request
    """
    dbs=None 
    try :
        username = request.form.get(constantes.s_USERNAME, default=None)
        password = request.form.get(constantes.s_PASSWORD, default=None)
        if username == None or password == None:
            flash("invalid authentification", constantes.s_FLASH_ERROR)
            raise Exception("at least one argument not included in the POST")
            
        dbs = db.get_session()
        if not dbs :
            flash("unreachable DataBase, please retry or contact the IT team", constantes.s_FLASH_ERROR)
            raise Exception("couldn't reach the database")
            
        with dbs.cursor() as dbc :
            dbc.execute("SELECT id, username, firstname, lastname, email, password_sha256_hexdigest, salt FROM users WHERE username = %s;", [username])
            
            answer = dbc.fetchone()
            if not answer :
                flash("incorrect username or password", constantes.s_FLASH_ERROR)
                raise Exception("wrong username or password")

            password_sha256_hashdigest = answer[5]
            salt = answer[6]
            salted_password = password+salt
            salted_password = salted_password.encode('utf-8')
            sha256_hashed_input = hashlib.sha256(salted_password).hexdigest()
            if sha256_hashed_input != password_sha256_hashdigest :
                flash("incorrect username or password", constantes.s_FLASH_ERROR)
                raise Exception("wrong username or password")

            uid = answer[0]
            username = answer[1]
            firstname = answer[2]
            lastname = answer[3]
            email = answer[4]

            session[constantes.s_USERNAME] = username
            session[constantes.s_FIRSTNAME] = firstname
            session[constantes.s_LASTNAME] = lastname 
            session[constantes.s_UID] = uid 
            session[constantes.s_EMAIL] = email
            session[constantes.s_IS_LOGGED_IN] = True

            flash("successfully logged in", constantes.s_FLASH_SUCCESS)
            dbs.close()
            return redirect(url_for('home'))     
    except Exception as e :
        if dbs :
            dbs.close()
        flash("internal error : " + str(e), constantes.s_FLASH_ERROR) 
        return render_template("pages/login.html", data=data_4_jinja())

@app.route("/signup/", methods=["GET", "POST"])
def signup():
    """
    login verification
    """
    is_logged_in = session.get(constantes.s_IS_LOGGED_IN, default=False)
    if is_logged_in :
        return redirect(url_for('home'))
    
    """
    GET signup visual
    """
    if request.method == "GET":
        return render_template("pages/signup.html", data=data_4_jinja())

    """
    POST signup data
    """
    dbs = None  
    try:
        firstname = request.form.get(constantes.s_FIRSTNAME, default=None)
        lastname = request.form.get(constantes.s_LASTNAME, default=None)
        username = request.form.get(constantes.s_USERNAME, default=None)
        password = request.form.get(constantes.s_PASSWORD, default=None)
        email = request.form.get(constantes.s_EMAIL, default=None)

        if username == None or password == None or firstname == None or lastname == None or email == None:
            raise Exception("at least one argument not included in the POST")
       
        dbs = db.get_session()
        if not dbs :
            flash("unreachable DataBase, please retry or contact the IT team", constantes.s_FLASH_ERROR)
            raise Exception("couldn't reach the database")
        
        with dbs.cursor() as dbc :
            salt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
            print(salt)
            salted_password = password + salt
            password_sha256_hexdigest = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
            dbc.execute("INSERT INTO users(firstname, lastname, username, password_sha256_hexdigest, salt, email) VALUES (%s, %s, %s, %s, %s, %s);", (firstname, lastname, username, password_sha256_hexdigest, salt, email))
            dbs.commit()
            flash("successfully created account", constantes.s_FLASH_SUCCESS)
        
        dbs.close()
        return redirect(url_for("home"))
        
    except Exception as e :
        if dbs :
            dbs.close()
        flash("internal error : " + str(e), constantes.s_FLASH_ERROR)
        return render_template("pages/signup.html", data=data_4_jinja())

@app.route("/logout/")
def logout():
    """
    page functionality
    """
    session.clear()
    flash("successfully logged out", constantes.s_FLASH_SUCCESS)
    return redirect(url_for("home"))

@app.route("/my_images/")
def my_images():
    is_logged_in = session.get(constantes.s_IS_LOGGED_IN, default=None)
    if not is_logged_in :
        flash("you need to login first", constantes.s_FLASH_ERROR)
        return redirect(url_for("login"))
    
    user_id = session.get(constantes.s_UID)
    dbs = None
    data=data_4_jinja()
    try : 
        dbs = db.get_session()
        with dbs.cursor() as dbc :
            dbc.execute("SELECT filename, description, upload_at FROM images WHERE user_id = %s;", [user_id])
            data["images"] = dbc.fetchall()
    except Exception as e :
        if dbs :
            dbs.close()

    return render_template("pages/my_images.html", data=data)

@app.route("/my_scripts/")
def scripts():
    is_logged_in = session.get(constantes.s_IS_LOGGED_IN, default=None)
    if not is_logged_in :
        flash("you need to login first", constantes.s_FLASH_ERROR)
        return redirect(url_for("login"))

    data=data_4_jinja()
    
    # list all the available scripts
    user_id = session.get(constantes.s_UID)
    dbs = None
    data=data_4_jinja()
    try : 
        dbs = db.get_session()
        with dbs.cursor() as dbc :
            dbc.execute("SELECT filename, description, upload_at FROM scripts WHERE user_id = %s;", [user_id])
            data["scripts"] = dbc.fetchall()

    except Exception as e :
        flash(str(e))
        if dbs :
            dbs.close()

    return render_template("pages/my_scripts.html", data=data)

@app.route("/my_projects/")
def my_projects():
    is_logged_in = session.get(constantes.s_IS_LOGGED_IN, default=None)
    if not is_logged_in :
        flash("you need to login first", constantes.s_FLASH_ERROR)
        return redirect(url_for("login"))

    data=data_4_jinja()
    
    # list all the projects
    user_id = session.get(constantes.s_UID)
    dbs = None
    data=data_4_jinja()
    try : 
        dbs = db.get_session()
        with dbs.cursor() as dbc :
            dbc.execute("SELECT id, name, description FROM projects WHERE user_id = %s;", [user_id])
            data["projects"] = dbc.fetchall()
    except Exception as e :
        if dbs :
            dbs.close()

    return render_template("pages/my_projects.html", data=data)

@app.route("/project/<project_id>")
def project(project_id):
    is_logged_in = session.get(constantes.s_IS_LOGGED_IN, default=None)
    if not is_logged_in :
        flash("you need to login first", constantes.s_FLASH_ERROR)
        return redirect(url_for("login"))
    
    dbs = None 
    try : 
        dbs = db.get_session()
        with dbs.cursor() as dbc :
            dbc.execute("SELECT id, name, description FROM projects WHERE id = %s and user_id = %s;", (project_id, session[constantes.s_UID]))
            data = data_4_jinja()
            project_data = dbc.fetchone()
            
            if not project_data :
                flash("you do not have a project with the provided ID", constantes.s_FLASH_ERROR)
                raise Exception("no such project found")
             
            data["project_id"] = project_data[0]
            data["project_name"] = project_data[1]
            data["project_description"] = project_data[2]

            dbc.execute("SELECT s.sid, fb.posted_at, NOW() FROM servers as s LEFT JOIN servers_feedback as fb ON s.sid = fb.server_id AND s.project_id = fb.project_id WHERE s.project_id = %s;", [project_id])
            infrastructure = dbc.fetchall()
            if infrastructure : 
                servers = []
                for server in infrastructure :
                    server_info = {
                        "sid": server[0],
                        "status": "unknown"
                    }
                    if server[1]:
                        # parse mysql time format 
                        d1 = server[1]
                        d2 = server[2]
                        delta = abs(d1 - d2)
                        if delta.seconds < 60 :
                            server_info["status"] = "super-active"
                        elif delta.seconds < (5 * 60):
                            server_info["status"] = "active"
                        elif delta.seconds < (60*60) :
                            server_info["status"] = "within-hour"
                        else :
                            server_info["status"] = "inactive"

                    servers.append(server_info)
                data["infrastructure"] = servers
            return render_template("pages/project.html", data=data)
        
    except Exception as e :
        flash(str(e))
        if dbs :
            dbs.close()
        return redirect(url_for("my_projects"))

@app.route("/server/<project_id>/<server_id>", methods=["GET", "POST"])
def administration_of_server(project_id, server_id):
    is_logged_in = session.get(constantes.s_IS_LOGGED_IN, default=None)
    if not is_logged_in :
        flash("you need to login first", constantes.s_FLASH_ERROR)
        return redirect(url_for("login"))

    ## render the server informations 
    if request.method == "GET" :
        dbs = None 
        try : 
            dbs = db.get_session()
            with dbs.cursor() as dbc :
                dbc.execute("SELECT s.sid, s.join_date, NOW() FROM servers as s JOIN projects as p ON s.project_id = p.id  WHERE p.user_id = %s AND s.project_id = %s AND s.sid = %s;", (session[constantes.s_UID], project_id, server_id))
                server = dbc.fetchone()
                if not server : 
                    flash("no such server in any of your clusters", constantes.s_FLASH_ERROR) 
                    raise Exception("no such server")
            
                data = data_4_jinja()
                data["register_date"] = server[1]
                data["time"] = server[2]

                dbc.execute("SELECT posted_at FROM servers_feedback WHERE project_id = %s AND server_id = %s", (project_id, server_id))
                date = dbc.fetchone()
                if date :
                    data["latest_activity"] = date[0]

                dbc.execute("SELECT id, filename, description FROM images WHERE user_id = %s;", [session[constantes.s_UID]])
                images = dbc.fetchall()
                if images : 
                    data["images"] = images

                dbc.execute("SELECT id, filename, description FROM scripts WHERE user_id = %s;", [session[constantes.s_UID]])
                scripts = dbc.fetchall()
                if scripts : 
                    data["scripts"] = scripts
                
                dbc.execute("SELECT task_json FROM tasks WHERE project_id = %s AND server_id = %s AND completed = 0 ORDER BY id ASC;", (project_id, server_id))
                scheduled_tasks = dbc.fetchall()
                if scheduled_tasks :
                    tasks = []
                    for task in scheduled_tasks :
                        tasks.append(json.loads(task[0]))
                    data["scheduled_tasks"] = tasks
             
                dbc.execute("SELECT t.task_json, tf.task_feedback FROM tasks as t LEFT JOIN tasks_feedback as tf ON t.id = tf.task_id WHERE t.project_id = %s AND t.server_id = %s AND completed = 1 ORDER BY t.id ASC;", (project_id, server_id))
                completed_tasks = dbc.fetchall()
                if completed_tasks : 
                    t = []
                    for task in completed_tasks :
                        task_description = json.loads(task[0])
                        task_feedback = None 
                        if task[1]:
                            task_feedback = json.loads(task[1])
                        t.append((task_description, task_feedback))

                    data["completed_tasks"] = t

                data["sid"] = server[0]
                data["join_date"] = server[1]

                return render_template("pages/server.html", data=data)

        except Exception as e :
            flash(str(e), constantes.s_FLASH_ERROR)
            return redirect(url_for("my_projects"))

    ## submit of a task to be done by a server 
    dbs = None 
    try : 
        scriptId = request.form.get("script", default="")
        imageId = request.form.get("image", default="")

        if not scriptId and not imageId : 
            flash("invalid task statement", constantes.s_FLASH_ERROR)
            raise Exception("can not create such a task")

        dbs = db.get_session()
        with dbs.cursor() as dbc : 
            dbc.execute("SELECT s.sid FROM servers as s JOIN projects as p ON s.project_id = p.id  WHERE p.user_id = %s AND s.project_id = %s AND s.sid = %s;", (session[constantes.s_UID], project_id, server_id))
            server = dbc.fetchone()
            if not server : 
                flash("no such server in any of your clusters", constantes.s_FLASH_ERROR)
                raise Exception("no such server in your clusters")

            if imageId :
                ## See if the request image is hold by the current user 
                dbc.execute("SELECT filename FROM images WHERE id = %s AND user_id = %s;", (imageId, session[constantes.s_UID]))
                filename = dbc.fetchone()
                if not filename : 
                    flash("you have no such image", constantes.s_FLASH_ERROR)
                    raise Exception("you have no such image")
                
                ## grant access to the file to the server 
                dbc.execute("SELECT * FROM images_servers WHERE image_id = %s AND project_id = %s AND server_id = %s AND user_id = %s;", (imageId, project_id, server_id, session[constantes.s_UID]))
                access_already_granted = dbc.fetchone()
                if not access_already_granted :
                    dbc.execute("INSERT INTO images_servers(image_id, project_id, server_id, user_id) VALUES(%s, %s, %s, %s);", (imageId, project_id, server_id, session[constantes.s_UID]))

                ## finally register the task
                task_description = {
                    "task_type" : "download_image",
                    "file_id" : imageId,
                    "file_name" : filename[0]
                }
                task_json = json.dumps(task_description)
                dbc.execute("INSERT INTO tasks(project_id, server_id, task_json) VALUES(%s, %s, %s);", (project_id, server_id, task_json))
                dbs.commit()
                flash("successfully registered task", constantes.s_FLASH_SUCCESS)
                return redirect(url_for("administration_of_server", project_id=project_id, server_id=server_id))

            if scriptId :
                ## See if the request image is hold by the current user 
                dbc.execute("SELECT filename FROM scripts WHERE id = %s AND user_id = %s;", (scriptId, session[constantes.s_UID]))
                filename = dbc.fetchone()
                if not filename : 
                    flash("you have no such script", constantes.s_FLASH_ERROR)
                    raise Exception("you have no such script")
                
                ## grant access to the file to the server 
                dbc.execute("SELECT * FROM scripts_servers WHERE script_id = %s AND project_id = %s AND server_id = %s AND user_id = %s;", (scriptId, project_id, server_id, session[constantes.s_UID]))
                access_already_granted = dbc.fetchone()
                if not access_already_granted :
                    dbc.execute("INSERT INTO scripts_servers(script_id, project_id, server_id, user_id) VALUES(%s, %s, %s, %s);", (scriptId, project_id, server_id, session[constantes.s_UID]))

                capture_output = False
                if request.form.get("capture_output", default=""): 
                    capture_output = True

                ## finally register the task
                task_description = {
                    "task_type" : "execute_script",
                    "file_id" : scriptId,
                    "file_name" : filename[0],
                    "capture_output" : capture_output
                }
                task_json = json.dumps(task_description)
                dbc.execute("INSERT INTO tasks(project_id, server_id, task_json) VALUES(%s, %s, %s);", (project_id, server_id, task_json))
                dbs.commit()
                flash("successfully registered task", constantes.s_FLASH_SUCCESS)
                return redirect(url_for("administration_of_server", project_id=project_id, server_id=server_id))

    except Exception as e :
        if dbs :
            dbs.close()
        flash(str(e), constantes.s_FLASH_ERROR)
        return redirect(url_for("my_projects"))

@app.route("/new_project/", methods=["GET", "POST"])
def new_project():
    is_logged_in = session.get(constantes.s_IS_LOGGED_IN, default=None)
    if not is_logged_in :
        flash("you need to login first", constantes.s_FLASH_ERROR)
        return redirect(url_for("login"))
    
    if request.method == "GET":
        return render_template("pages/new_project.html", data=data_4_jinja())
    
    """
    Register the project in the DataBase 
    """
    dbs = None 
    try : 
        project_name = request.form.get("project_name", default="")
        project_description = request.form.get("project_description", default="")
        if project_name == "" :
            flash("empty project name not allowed", constantes.s_FLASH_ERROR)
            raise Exception("empty project name not allowed")

        dbs = db.get_session()
        with dbs.cursor() as dbc :
            dbc.execute("INSERT INTO projects(name, description, user_id) VALUES(%s, %s, %s);", (project_name, project_description, session[constantes.s_UID]))
            project_id = dbc.lastrowid

            try : 
                ## after registering the image in the DataBase, create 
                ## a client bundle for the given project in the filesystem 
                payload = {
                    "pid" : project_id
                }
                token = jwt.encode(payload, os.getenv("TOKEN_SIGNING_SECRET"), algorithm="HS256")
                
                user_path = f"/user_files/user_{session[constantes.s_UID]}"
                if not os.path.exists(user_path):
                    os.mkdir(user_path)

                project_path = f"{user_path}/project_{project_id}"
                if not os.path.exists(project_path):
                    os.mkdir(project_path)

                archieve_path = f"{project_path}/client_bundle"
                if not os.path.exists(archieve_path):
                    os.mkdir(archieve_path)
                
                # save the token as a file in the bundle 
                with open(f"{archieve_path}/token", "w") as f:
                    f.write(token)

                # save the host ip as a file in the bundle
                with open(f"{archieve_path}/hostname", "w") as f:
                    f.write(f"{os.getenv('API_SERVER_IP')}")

                # copy the certificate 
                shutil.copy(f"/server_ssl/server.crt", f"{archieve_path}/server.crt") 

                # copy the client python script 
                shutil.copy(f"/generic_client_bundle/client.py", f"{archieve_path}/client.py") 

                # copy the systemd service
                shutil.copy(f"/generic_client_bundle/kapitan_client.service", f"{archieve_path}/kapitan_client.service") 

                # build the client bundle archive 
                shutil.make_archive(archieve_path,"zip",archieve_path)

                dbs.commit()
                flash(f"successfull project creation", constantes.s_FLASH_SUCCESS)
                return redirect(url_for("my_projects"))
    
            except Exception as e : 
                flash(str(e), constantes.s_FLASH_ERROR)
                flash("failed to create the client bundle", constantes.s_FLASH_ERROR)
                raise Exception("failed to create the client bundle")

    except Exception as e : 
        if dbs :
            dbs.close()
        flash(str(e), constantes.s_FLASH_ERROR)
        return render_template("pages/new_project.html", data=data_4_jinja())

@app.route("/get_client_bundle/<project_id>")
def get_client_bundle(project_id):
    is_logged_in = session.get(constantes.s_IS_LOGGED_IN, default=None)
    if not is_logged_in :
        flash("you need to login first", constantes.s_FLASH_ERROR)
        return redirect(url_for("login"))
    
    dbs = None 
    try :
        dbs = db.get_session()
        with dbs.cursor() as dbc :
            dbc.execute("SELECT * FROM projects WHERE user_id = %s AND id = %s", (session[constantes.s_UID], project_id))
            
            project = dbc.fetchone()
            if not project : 
                flash("you have no project with such an ID", constantes.s_FLASH_ERROR)
                raise Exception("invalid error")

            archieve_path = f"/user_files/user_{session[constantes.s_UID]}/project_{project_id}/client_bundle.zip"
            if not os.path.exists(archieve_path):
                flash("client bundle not found", constantes.s_FLASH_ERROR)
                raise Exception("client bundle not found")
            
            return send_file(archieve_path)

    except Exception as e:
        if dbs :
            dbs.close()
        flash(str(e), constantes.s_FLASH_ERROR)
        return redirect(url_for("my_projects"))
    
@app.route("/upload_image/", methods=["GET", "POST"])
def upload_image():
    is_logged_in = session.get(constantes.s_IS_LOGGED_IN, default=None)
    if not is_logged_in :
        flash("you need to login first", constantes.s_FLASH_ERROR)
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("pages/upload_image.html", data=data_4_jinja())
    
    """
    Create the user image folder, if it
    does not already exist 
    """
    user_path = f"/user_files/user_{session[constantes.s_UID]}"
    if not os.path.exists(user_path):
        os.mkdir(user_path)

    image_path = f"{user_path}/images/"
    if not os.path.exists(image_path):
        os.mkdir(image_path)

    """
    Register the image in the DataBase 
    """
    dbs = None 
    try : 
        image = request.files['image']
        if not image.filename :
            flash("no file provided", constantes.s_FLASH_ERROR)
            raise Exception("no file provided")
        
        image_name = image.filename
        description = request.form.get("description", default="")
        user_id = session.get(constantes.s_UID)

        dbs = db.get_session()
        with dbs.cursor() as dbc :
            dbc.execute("INSERT INTO images(filename, description, upload_at, user_id) VALUES(%s, %s, NOW(), %s);", (image_name, description, user_id))
            image_id = dbc.lastrowid 

            ## after registering the image in the DataBase, save the image in the file tree 
            image.save(f"{image_path}/image_{image_id}")
            dbs.commit()
            flash(f"successfull import of {image.filename}", constantes.s_FLASH_SUCCESS)
            return redirect(url_for("my_images"))

    except Exception as e : 
        if dbs :
            dbs.close()
        flash("couldn't upload image", constantes.s_FLASH_ERROR)
        return render_template("pages/upload_image.html")

@app.route("/upload_script/", methods=["GET", "POST"])
def upload_script():
    is_logged_in = session.get(constantes.s_IS_LOGGED_IN, default=None)
    if not is_logged_in :
        flash("you need to login first", constantes.s_FLASH_ERROR)
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("pages/upload_script.html", data=data_4_jinja())

    """
    Create the user script folder, if it
    does not already exist 
    """
    user_path = f"/user_files/user_{session[constantes.s_UID]}"
    if not os.path.exists(user_path):
        os.mkdir(user_path)

    script_path = f"{user_path}/scripts/"
    if not os.path.exists(script_path):
        os.mkdir(script_path)

    """
    Register the script in the DataBase 
    """
    dbs = None 
    try : 
        script = request.files['script']
        if not script.filename :
            flash("no file provided", constantes.s_FLASH_ERROR)
            raise Exception("no file provided")
        
        script_name = script.filename
        description = request.form.get("description", default="")
        user_id = session.get(constantes.s_UID)

        dbs = db.get_session()
        with dbs.cursor() as dbc :
            dbc.execute("INSERT INTO scripts(filename, description, upload_at, user_id) VALUES(%s, %s, NOW(), %s);", (script_name, description, user_id))
            script_id = dbc.lastrowid 

            ## after registering the image in the DataBase, save the image in the file tree 
            script.save(f"{script_path}/script_{script_id}")
            dbs.commit()
            flash(f"successfull import of {script.filename}", constantes.s_FLASH_SUCCESS)
            return redirect(url_for("scripts"))

    except Exception as e : 
        if dbs :
            dbs.close()
        flash(str(e), constantes.s_FLASH_ERROR)
        return render_template("pages/upload_script.html", data=data_4_jinja())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5454, debug=True)