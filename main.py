from flask import *
from flask_dropzone import Dropzone
import os
import time
from datetime import datetime
import tarfile


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.update(
    UPLOADED_PATH= os.path.join(basedir,'uploads'),
    DROPZONE_MAX_FILE_SIZE = 1024,
    DROPZONE_TIMEOUT = 5*60*1000
)

dropzone = Dropzone(app)

# Placeholder link
@app.route('/chat',methods=['POST','GET'])
def chat():
    return "Hello chat"


@app.route('/create',methods=['POST','GET'])
def create():
    #if passcode is available in files then redirect to the
    #confirm page while sending the chat name and password to confirm
    return render_template('create.html', template_folder='templates')


@app.route('/select',methods=['POST','GET'])
def select():
    return render_template('select.html', template_folder='templates')


@app.route('/')
def hello():
    return render_template('index.html', template_folder='templates')

if __name__=='__main__':
    app.run()

