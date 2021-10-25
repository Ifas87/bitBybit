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

@app.route('/upload',methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'],f.filename))
    return render_template('upload.html', template_folder='templates')

@app.route('/uploader',methods=['POST','GET'])
def download_manager():
    my_files = request.files
    current_time = datetime.now()
    temp_filename = "file_"+current_time.strftime("%m_%d_%Y_%H_%M_%S_%f")+"_package.tar.gz"

    tar = tarfile.open("uploads/"+temp_filename, mode="w:gz")
    for item in my_files:
        uploaded_file = my_files.get(item)
        tarlocation = os.path.join(app.config['UPLOADED_PATH']+"/temp", item.filename)
        item.save(tarlocation)
        tar.add(tarlocation)
    
    tar.close()
    return redirect(url_for('hello'))


@app.route('/')
def hello():
    return render_template('index.html', template_folder='templates')

if __name__=='__main__':
    app.run()
