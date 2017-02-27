import os
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def root():
    return app.send_static_file('index.html')



@app.route('/print', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        print ("'name = '{}' email = '{}' nametag_img = '{}'".format( str(request.form['name']), str(request.form['email']), str(request.form['nametag_img']) ) )
        return "OK"
    else:
        return "Working"


app.run(host= '0.0.0.0')
