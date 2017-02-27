import os, base64, csv, datetime
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_user_info(name, email):
    needs_header = False
    if not os.path.exists("userInformation.csv"):
        needs_header = True

    with open("userInformation.csv", 'a') as csvfile:
        fieldnames = ["Name", "Email", "Timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if needs_header:
            writer.writeheader()
        writer.writerow({"Name":name, "Email":email, "Timestamp":datetime.datetime.now()})


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/print', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        print ("'name = '{}' email = '{}' nametag_img = '{}'".format( str(request.form['name']), str(request.form['email']), str(request.form['nametag_img']) ) )
        with open("temp.png", "wb") as f:
            # Removing the prefix 'data:image/png;base64,'
            data = request.form['nametag_img'].split(",")[1]
            f.write(base64.b64decode(data))
        save_user_info(request.form['name'], request.form['email'])
        return "OK"
    else:
        return "Working"


app.run(host= '0.0.0.0')
