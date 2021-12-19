from flask import *
from flask_dropzone import Dropzone
import os
import time
import sys
from datetime import datetime
import tarfile
import secrets
import re


FILESYSTEM_dir = r"C:\Users\Safi\Desktop\Safi\Year 3\CST 3590 Individual Project\Project files\bitBybit v2\content"
PATH_chats = r"C:\Users\Safi\Desktop\Safi\Year 3\CST 3590 Individual Project\Project files\bitBybit v2\content\chatrooms.txt"
ERR_pass = "Wrong passcode provided!"
ERR_room = "No room by that name present!"
ERR_word = "Room names are only one word long!"
ERR_same = "Room with that name already exists!"

newRoomRegex = "^(\w+)$"
customPath = r""

basedir = os.path.abspath(os.path.dirname(__file__))

"""
    timestr = time.strftime("%Y%m%d-%H%M%S")
    print(timestr)
"""

app = Flask(__name__)
app.config.update(
    UPLOADED_PATH= os.path.join(basedir,'uploads'),
    DROPZONE_MAX_FILE_SIZE = 1024,
    DROPZONE_TIMEOUT = 5*60*1000
)

secret = secrets.token_urlsafe(32)
app.secret_key = secret

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
                    allRoomNames.append(line.split()[0].strip())
                    line = f.readline()

        reg = re.compile( r'^(?=.*\b(?:' + "|".join(allRoomNames) + r')\b).*foo' )

        if(re.search(newRoomRegex, room)):
            # Search for existing rooms with the same name
            if(reg.findall(room)):
                flash(ERR_same)
                return redirect(url_for('create'))
            
            session["current_room"] = room
            with open(PATH_chats, "a", encoding = 'utf-8') as f:
                f.write("{} : {}\n".format(room, passcode))
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


@app.route('/')
def hello():
    session["current_room"] = "placeholder"
    return render_template('index.html', template_folder='templates')


# Placeholder link
@app.route('/chat',methods=['POST','GET'])
def chat():
    keyCount = 0

    chat_content = {}
    roomname = session["current_room"]
    customPath = "" + FILESYSTEM_dir + "/" + roomname

    print(FILESYSTEM_dir)
    directory = os.fsencode(FILESYSTEM_dir)
    
    for file in os.listdir(customPath):
        filename = os.fsdecode(file)
        print(filename)
        if filename.endswith(".txt"): 
            with open((customPath + "/" + filename), "r", encoding = 'utf-8') as f:
                data = f.read().replace('\n', ' ')
            chat_content[("tEXt"+str(keyCount))] = data
            keyCount+=1

        elif filename.endswith(".zip") or filename.endswith('.tar.gz'):
            chat_content[filename] = (customPath + "/" + filename)
            keyCount+=1
        
        print(chat_content)
    return render_template('chat_template.html', template_folder='templates', var=roomname, dict_item=chat_content)


if __name__=='__main__':
    app.run()

