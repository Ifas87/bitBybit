from flask import *
from flask_dropzone import Dropzone
import os
import time
import sys
from datetime import datetime
import tarfile
import secrets


FILESYSTEM_dir = r"C:\Users\Safi\Desktop\Safi\Year 3\CST 3590 Individual Project\Project files\bitBybit v2\content"
PATH_chats = r"C:\Users\Safi\Desktop\Safi\Year 3\CST 3590 Individual Project\Project files\bitBybit v2\content\chatrooms.txt"
ERR_pass = "Wrong passcode provided!"
ERR_room = "No room by that name present!"

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

dropzone = Dropzone(app)

# Placeholder link
@app.route('/chat',methods=['POST','GET'])
def chat():
    roomname = session["current_room"]
    return render_template('chat_template.html', template_folder='templates', var=roomname)

@app.route('/create',methods=['POST','GET'])
def create():
    #if passcode is available in files then redirect to the
    #confirm page while sending the chat name and password to confirm
    #^\w+$

    print("here")
    if request.method == 'POST':
        room = request.form.get('links')
        passcode = request.form.get('passcodes')
        duration = request.form.get('TTL')
        print(room, passcode, duration)

        with open(PATH_chats, "a", encoding = 'utf-8') as f:
            f.write("{} : {}\n".format(room, passcode))
    return render_template('create.html', template_folder='templates')


@app.route('/select',methods=['POST','GET'])
def select():
    print("here")
    if request.method == 'POST':
        room = request.form.get('links')
        passcode = request.form.get('passcodes')
        print(room, passcode, file=sys.stderr)

        with open(PATH_chats, encoding = 'utf-8') as f:
            line = f.readline()
            while line:
                if(line.split(" : ")[0] == room):
                    if (line.split(" : ")[1] == passcode):
                        print("Success")
                        session["current_room"] = room
                        return redirect(url_for('chat'))
                    else:
                        flash(ERR_pass)
                        line = f.readline()
                        return redirect(url_for('select'))
                else:
                    flash(ERR_room)
                    line = f.readline()
                    return redirect(url_for('select'))
                
    return render_template('select.html', template_folder='templates')


@app.route('/')
def hello():
    return render_template('index.html', template_folder='templates')

if __name__=='__main__':
    app.run()

