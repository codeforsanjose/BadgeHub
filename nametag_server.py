import os, sys, base64, csv, datetime
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

PAGE_SIZE = "Custom.54x100mm"
IMAGE_FILE = "temp.png"
CSV_FILE = "userInformation.csv"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)


def get_script_path():
    """
    http://stackoverflow.com/a/4943474
    """
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_user_info(name, email):
    needs_header = False
    csv_file = os.path.join(os.sep, get_script_path(), CSV_FILE)
    print("using CSV file at {}".format(csv_file))
    if not os.path.exists(csv_file):
        needs_header = True

    with open(csv_file, 'a') as csvfile:
        fieldnames = ["Name", "Email", "Timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if needs_header:
            writer.writeheader()
        writer.writerow({"Name":name, "Email":email, "Timestamp":datetime.datetime.now()})

def send_to_printer():
    print("sending image to printer")
    img_file = os.path.join(os.sep, get_script_path(), IMAGE_FILE)
    os.system("lpr -o landscape -o PageSize={} -o fit-to-page  {}".format(PAGE_SIZE, img_file))

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/printing')
def printing():
    return app.send_static_file('printing.html')

@app.route('/print', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        print ("'name = '{}' email = '{}' nametag_img = '{}'".format( str(request.form['name']), str(request.form['email']), str(request.form['nametag_img']) ) )
        img_file = os.path.join(os.sep, get_script_path(), IMAGE_FILE)
        print("saving temp image at {}".format(img_file))
        with open(img_file, "wb") as f:
            # Removing the prefix 'data:image/png;base64,'
            data = request.form['nametag_img'].split(",")[1]
            f.write(base64.b64decode(data))
        save_user_info(request.form['name'], request.form['email'])
        send_to_printer()
        return redirect(url_for("printing"))


app.run(host= '0.0.0.0')
