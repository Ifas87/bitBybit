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


FILESYSTEM_dir = r"C:\Users\Safi\Desktop\Safi\Year 3\CST 3590 Individual Project\Project files\bitBybit v2\content"
PATH_chats = r"C:\Users\Safi\Desktop\Safi\Year 3\CST 3590 Individual Project\Project files\bitBybit v2\content\chatrooms.txt"
ERR_pass = "Wrong passcode provided!"
ERR_room = "No room by that name present!"
ERR_word = "Room names are only one word long!"
ERR_same = "Room with that name already exists!"

current_chat = ""
newRoomRegex = "^(\w+)$"
customPath = r""

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.update(
    UPLOADED_PATH= os.path.join(basedir,'content')
)

app.config['UPLOAD_FOLDER'] = FILESYSTEM_dir

secret = secrets.token_urlsafe(32)
app.secret_key = secret

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
            os.rmdir(FILESYSTEM_dir + "/" + chatname)
            return redirect(url_for('create'))
        else:
            print("not same")
            os.rmdir(FILESYSTEM_dir + "/" + chatname)
        
    with open(PATH_chats, 'r') as read_file:
        lines = read_file.readlines()
        print(lines)

    with open(PATH_chats, 'w') as write_file:
        for line in lines:
            if chatname in line:
                continue
            write_file.write(line)


@app.route('/downloader/', methods=['POST', 'GET'])
def retreive():
    filename = request.args.get('data-status')
    return send_file(filename)


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
            os.mkdir((FILESYSTEM_dir+"/"+room))
            with open(PATH_chats, "a", encoding = 'utf-8') as f:
                f.write("{} : {}\n".format(room, passcode))
            
            thread = Thread(target = timer, args = (10, room))
            thread.start()
            
            return redirect(url_for('chat'))
        else:
            flash(ERR_word)
            return redirect(url_for('create'))
    return render_template('create.html', template_folder='templates')


@app.route('/options',methods=['POST','GET'])
def options():        
    return render_template('options.html', template_folder='templates')


@app.route('/versions',methods=['POST','GET'])
def versions():        
    return render_template('versions.html', template_folder='templates')


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


@app.route('/')
def hello():
    session["current_room"] = "placeholder"
    return render_template('index.html', template_folder='templates')


@app.route('/updater', methods=['POST','GET'])
def update():
    if request.method == 'POST':
        roomname = request.get_data()
        customPath = "" + FILESYSTEM_dir + "/" + roomname
        keyCount = 0
        chat_content = {}

        if os.path.exists(customPath):
            for file in os.listdir(customPath):
                filename = os.fsdecode(file)
                if filename.endswith(".txt"): 
                    with open((customPath + "/" + filename), "r", encoding = 'utf-8') as f:
                        data = f.read().replace('\n', ' ')
                    chat_content[("tEXt"+str(keyCount))] = data
                    keyCount+=1

                else:
                    chat_content[filename] = (customPath + "/" + filename)
                    keyCount+=1
        
        else:
            chat_content["DELETED"] = "".format('"{}" timer has expired ', roomname)

        return json.dumps(chat_content)


@app.route('/chat',methods=['POST','GET'])
def chat():
    roomname = session["current_room"]
    customPath = "" + FILESYSTEM_dir + "/" + roomname
    global current_chat
    current_chat = session["current_room"]

    if request.method == 'POST':
        text = request.form.get('chatarea')
        if not text == "":
            timestr = time.strftime("%Y%m%d-%H%M%S") + ".txt"
            with open((customPath+"/"+timestr), "w") as f:
                f.write(text)
        

        if request.files.getlist("files") or not any(f for f in request.files.getlist("files")):
        #if request.files.getlist("files"):
            files = request.files.getlist("files")
            for file in files:
                print("filename: ", file.filename)
                #file.save((customPath + "/" + file.filename))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], (roomname+"/"+file.filename)))

    keyCount = 0
    chat_content = {}

    directory = os.fsencode(FILESYSTEM_dir)
    
    for file in os.listdir(customPath):
        filename = os.fsdecode(file)
        if filename.endswith(".txt"): 
            with open((customPath + "/" + filename), "r", encoding = 'utf-8') as f:
                data = f.read().replace('\n', ' ')
            chat_content[("tEXt"+str(keyCount))] = data
            keyCount+=1

        else:
            chat_content[filename] = (customPath + "/" + filename)
            keyCount+=1
        
    return render_template('chat_template.html', template_folder='templates', var=roomname, dict_item=chat_content)


if __name__=='__main__':
    app.run()

