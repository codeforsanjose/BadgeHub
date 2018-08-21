import os, sys, base64, csv, datetime, logging
from config import CSV_FILENAME, LOGGING_ID
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename

PAGE_SIZE = "Custom.54x100mm"
IMAGE_FILE = "temp.png"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
logger = logging.getLogger(LOGGING_ID)

def get_script_path():
    """
    http://stackoverflow.com/a/4943474
    """
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_user_info(name, pronoun, email):
    needs_header = False
    csv_file = os.path.join(os.sep, get_script_path(), CSV_FILENAME)
    logger.info("using CSV file at {}".format(csv_file))
    if not os.path.exists(csv_file):
        needs_header = True

    with open(csv_file, 'a') as csvfile:
        fieldnames = ["Name", "Pronoun", "Email", "Timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if needs_header:
            writer.writeheader()
        writer.writerow({"Name":name, "Preferred Pronoun":pronoun, "Email":email, "Timestamp":datetime.datetime.now()})

def send_to_printer():
    logger.info("sending image to printer")
    img_file = os.path.join(os.sep, get_script_path(), IMAGE_FILE)
    os.system("lpr -o landscape -o PageSize={} -o fit-to-page  {}".format(PAGE_SIZE, img_file))

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/signin', methods=['POST'])
def signin():
    if request.method == 'POST':
        logger.info("'name = '{}' pronoun = '{}' email = '{}' nametag_img = '{}'".format( str(request.form['name']), str(request.form['pronoun']), str(request.form['email']), str(request.form['nametag_img']) ) )
        img_file = os.path.join(os.sep, get_script_path(), IMAGE_FILE)
        logger.info("saving temp image at {}".format(img_file))
        with open(img_file, "wb") as f:
            # Removing the prefix 'data:image/png;base64,'
            data = request.form['nametag_img'].split(",")[1]
            f.write(base64.b64decode(data))
        save_user_info(request.form['name'], request.form['pronoun'], request.form['email'])

        # print only if the submit button value is "print"
        if request.form['button'] == "print":
            logger.info("Printing nametag for \"%s\""%request.form['name'])
            send_to_printer()
            return render_template("thankyou.html", message="Your nametag will print soon.")

        # otherwise simply submit 
        elif request.form['button'] == "noprint":
            logger.info("Not printing for \"{}\"".format(request.form['name']))
            return render_template("thankyou.html", message="Successfully signed in, enjoy your hack night!")


def start_webserver():
    app.run(host= '0.0.0.0')

if __name__ == "__main__":
    start_webserver()

