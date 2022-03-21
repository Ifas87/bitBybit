from flask import *
from flask_dropzone import Dropzone
import os
import time
import sys
from datetime import datetime
import tarfile
import secrets
import re
from threading import Thread
import shutil



current_chat = ""
newRoomRegex = "^(\w+)$"
customPath = r""

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.update(
    UPLOADED_PATH= os.path.join(basedir,'content')
)

PATH_chats = app.config["UPLOADED_PATH"] + r"\chatrooms.txt"
PATH_tempfiles = app.config["UPLOADED_PATH"] + r"\temp"
ERR_pass = "Wrong passcode provided!"
ERR_room = "No room by that name present!"
ERR_word = "Room names are only one word long!"
ERR_same = "Room with that name already exists!"

secret = secrets.token_urlsafe(32)
app.secret_key = secret


def switchFiletoFolder(filename, olddelim, newdelim):
    if olddelim in filename:
        real_type = filename.split(olddelim)[0] + newdelim + filename.split(olddelim)[1]
    else:
        real_type = filename
    return real_type


def remover(complete_path):
    pass


def getVersion(filename):
    return os.path.splitext(filename)[0]


def lister(dir_path):
    result = []
    for file in os.listdir(dir_path):
        result.append(os.fsdecode(file))
    
    return result


def extract_file_number(f):
    s = re.findall("\d{1,3}",f)
    return (int(s[0]) if s else -1,f)


def timer(t, chatname):
    time.sleep(3)
    print(current_chat, chatname)
    with app.app_context(), app.test_request_context():
        while t:
            time.sleep(1)
            t -= 1
            print(t)
    
        if current_chat == chatname:
            print("same")
            os.rmdir(app.config["UPLOADED_PATH"] + "/" + chatname)
        else:
            print("not same")
            os.rmdir(app.config["UPLOADED_PATH"] + "/" + chatname)
    
    with open(PATH_chats, "r") as f:
        lines = f.readlines()
    with open(PATH_chats, "w") as f:
        for line in lines:
            print(line)
            if chatname not in line.strip("\n"):
                f.write(line)



@app.route('/')
def hello():
    session["current_room"] = "placeholder"
    return render_template('index.html', template_folder='templates')



@app.route('/create',methods=['POST','GET'])
def create():
    print("here")
    if request.method == 'POST':
        room = request.form.get('links')
        passcode = request.form.get('passcodes')
        duration = request.form.get('TTL')
        allRoomNames = []

        with open(PATH_chats, encoding = 'utf-8') as f:
            line = f.readline()
            while line:
                allRoomNames.append(line.split(":")[0].strip())
                line = f.readline()

        reg = re.compile( r'^(?=.*\b(?:' + "|".join(allRoomNames) + r')\b).*foo' )

        if(re.search(newRoomRegex, room)):
            if(reg.findall(room)):
                flash(ERR_same)
                return redirect(url_for('create'))
            
            session["current_room"] = room
            os.mkdir((app.config["UPLOADED_PATH"]+"/"+room))
            with open(PATH_chats, "a", encoding = 'utf-8') as f:
                f.write("{} : {}\n".format(room, passcode))
            
            if(not(duration >= 20000)):
                thread = Thread(target = timer, args = (10, room)) # !!!! Change this line in code to the value of the TTL dropdown box 
                thread.start()
            
            return redirect(url_for('chat'))
        else:
            flash(ERR_word)
            return redirect(url_for('create'))
    return render_template('create.html', template_folder='templates')



@app.route('/select',methods=['POST','GET'])
def select():
    print("here")
    if request.method == 'POST':
        room = request.form.get('links')
        passcode = request.form.get('passcodes')
        print(room + " : " + passcode)

        with open(PATH_chats, encoding = 'utf-8') as f:
            line = f.readline()
            print(line.split(" : ")[0] + " : " + line.split(" : ")[1])
            while line:
                if(line.split(" : ")[0] == room):
                    if not (line.split(" : ")[1]).strip():
                        print("Success")
                        session["current_room"] = room
                        return redirect(url_for('chat'))
                    
                    else:
                        if ((line.split(" : ")[1]).strip() == passcode):
                            print("Success")
                            session["current_room"] = room
                            return redirect(url_for('chat'))
                        else:
                            flash(ERR_pass)
                            line = f.readline()
                            return redirect(url_for('select'))
                else:
                    line = f.readline()
                    continue

            flash(ERR_room)
            return redirect(url_for('select'))
                
    return render_template('select.html', template_folder='templates')
 


@app.route('/chat',methods=['POST','GET'])
def chat():
    roomname = session["current_room"]
    customPath = "" + app.config["UPLOADED_PATH"] + "/" + roomname
    global current_chat
    current_chat = session["current_room"]

    if request.method == 'POST':
        text = request.form.get('chatarea')
        if not text == "":
            timestr = time.strftime("tEXt%Y%m%d-%H%M%S") + ".txt"
            with open((customPath+"/"+timestr), "w") as f:
                f.write(text)

    keyCount = 0
    chat_content = {}

    directory = os.fsencode(app.config["UPLOADED_PATH"])
    
    for file in os.listdir(customPath):
        filename = os.fsdecode(file)
        if filename.startswith("tEXt"): 
            with open((customPath + "/" + filename), "r", encoding = 'utf-8') as f:
                data = f.read().replace('\n', ' ')
            chat_content[("tEXt"+str(keyCount))] = data
            keyCount+=1

        if(os.path.isdir(customPath+"/"+filename)):
            inner_dir_path = customPath + r"\\" + filename
            inner_dir_path_contents = lister(inner_dir_path)
            
            inner_latest_file = max(inner_dir_path_contents, key=extract_file_number)

            real_filename = switchFiletoFolder(filename, "-", ".")

            chat_content[real_filename+": Version "+getVersion(inner_latest_file)] = (inner_dir_path) 

        else:
            chat_content[filename] = (customPath + "/" + filename)
            keyCount+=1
        
    return render_template('chat_template.html', template_folder='templates', var=roomname, dict_item=chat_content)



@app.route('/options',methods=['POST','GET'])
def options():
    roomname = session["current_room"]
    customPath = r"" + app.config["UPLOADED_PATH"] + r"\\" + roomname
    dir_contents = []
    inner_dir_path = r""

    dir_contents = lister(customPath)

    if request.method == 'POST':
        checks = request.form.get("switch")

        if request.files.getlist("files"):
            files = request.files.getlist("files")
            folder_name=""

            if checks:
                archive = tarfile.open(".tar.gz", "w|gz")
            else:
                for file in files:
                    folder_name = switchFiletoFolder(file.filename, ".", "-")

                    inner_dir_path = customPath + r"\\" + folder_name
                    
                    if folder_name in dir_contents:
                        inner_dir_path_contents = lister(inner_dir_path)

                        inner_dir_path_contents = [int(x.split(".")[0]) if "." in file.filename else int(x.split(".")) for x in inner_dir_path_contents]
                        temp_version = str(max(inner_dir_path_contents)+1)

                        file.save(os.path.join(app.config['UPLOADED_PATH'],
                            (roomname+"/"+folder_name+"/"+ ( str(temp_version)+"."+(file.filename.split(".")[1] if "." in file.filename else file.filename)) ) ))
                        
                        return redirect(url_for('chat'))
                    else:
                        os.mkdir(inner_dir_path)
                        file.save(os.path.join(app.config['UPLOADED_PATH'], 
                            (roomname+"/"+folder_name+"/"+ ("1." +(file.filename.split(".")[1] if "." in file.filename else file.filename) ) )))

                        return redirect(url_for('chat'))

    return render_template('options.html', template_folder='templates')



@app.route('/versions/',methods=['POST','GET'])
def versions():
    if request.method == 'POST':
        folder_name = session["parent_directory"]
        filename = request.form.get("versions")

        original_name = os.path.basename(folder_name + "/" + switchFiletoFolder(os.path.basename(folder_name), "-", "."))
        return send_file((folder_name+"/"+filename), as_attachment=True, download_name=original_name)
    
    folder_name = request.args.get('data-status')
    session["parent_directory"] = folder_name
    result = lister(folder_name)

    return render_template('versions.html', template_folder='templates', versions = result)


"""
@app.route('/downloader/', methods=['POST', 'GET'])
def retreive():
    filename = request.args.get('data-status')
    return send_file(filename)
"""



@app.route('/updater', methods=['POST','GET'])
def update():
    if request.method == 'POST':
        roomname = str(request.get_data()).split("/")[1]
        customPath = r"" + app.config["UPLOADED_PATH"] + r"\\" + (str(roomname)[:-1])
        keyCount = 0
        chat_content = {}

        if os.path.exists(customPath):
            for file in os.listdir(customPath):
                filename = os.fsdecode(file)
                if filename.startswith("tEXt"): 
                    with open((customPath + "/" + filename), "r", encoding = 'utf-8') as f:
                        data = f.read().replace('\n', ' ')
                    chat_content[("tEXt"+str(keyCount))] = data
                    keyCount+=1

                if(os.path.isdir(customPath+"/"+filename)):
                    inner_dir_path = customPath + r"\\" + filename
                    inner_dir_path_contents = lister(inner_dir_path)
                    
                    inner_latest_file = max(inner_dir_path_contents, key=extract_file_number)

                    real_filename = switchFiletoFolder(filename, "-", ".")

                    chat_content[real_filename+": Version "+getVersion(inner_latest_file)] = (inner_dir_path) 

                else:
                    chat_content[filename] = (customPath + "/" + filename)
                    keyCount+=1

        else:
            chat_content["DELETED"] = "".format('"{}" timer has expired ', roomname)

        return json.dumps(chat_content)


if __name__=='__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))

