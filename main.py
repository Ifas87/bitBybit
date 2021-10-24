from flask import *
from flask_dropzone import Dropzone
import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.update(
    UPLOADED_PATH= os.path.join(basedir,'uploads'),
    DROPZONE_MAX_FILE_SIZE = 1024,
    DROPZONE_TIMEOUT = 5*60*1000
)

dropzone = Dropzone(app)

@app.route('/upload',methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'],f.filename))
    return render_template('upload.html', template_folder='templates')

@app.route('/')
def hello():
    return render_template('index.html', template_folder='templates')

if __name__=='__main__':
    app.run()
