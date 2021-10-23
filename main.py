from flask import *

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html', template_folder='templates')

if __name__=='__main__':
    app.run()
