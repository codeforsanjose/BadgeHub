import base64
import configparser
import csv
import datetime
import json
import logging
import os

# from werkzeug.utils import secure_filename
# from nfc import getBoardInfo
import redis
from flask import Flask, request, render_template, jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import BooleanField, StringField, TextAreaField
from wtforms.fields.html5 import DecimalRangeField
from wtforms.validators import NumberRange

from BadgeHub.config import CSV_FILENAME, DEBUG, PORT_NUMBER, REDIS_HOST, REDIS_PORT
from BadgeHub.image_creator import Nametag
from BadgeHub.redis_helper import get_preferences
from BadgeHub.utils import get_script_path
from BadgeHub.printer_manager import send_to_printer

PAGE_SIZE = "Custom.54x100mm"
IMAGE_FILE = "temp.png"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset="utf-8", db=0, decode_responses=True)
config = configparser.ConfigParser()

app = Flask(__name__)
logger = logging.getLogger(__name__)
app.config['SECRET_KEY'] = 'secret!'

last_server_status = {}
open_connections = 0

if DEBUG:
    logger.info("DEBUG mode enabled; enabling CORS for all requests")
    from flask_cors import CORS

    CORS(app)
else:
    logger.info("CORS is disabled")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_user_info(name, pronoun, email):
    needs_header = False
    logger.info("using CSV file at {}".format(CSV_FILENAME))
    if not os.path.exists(CSV_FILENAME):
        needs_header = True
    with open(CSV_FILENAME, 'a') as csvfile:
        fieldnames = ["Name", "Pronoun", "Email", "Timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if needs_header:
            writer.writeheader()
        writer.writerow({"Name": name, "Pronoun": pronoun, "Email": email, "Timestamp": datetime.datetime.now()})


@app.route('/')
def root():
    current_preferences = get_preferences(r)

    if current_preferences is None or all(value is None for value in current_preferences.values()):
        logger.info("Unexpected blank value for preferences")

    return render_template('index.html', preferences=current_preferences)



def setPreferences(prefs_dict):
    json_prefs = json.dumps(prefs_dict)
    logger.debug("setting preferences: {}".format(json_prefs))
    r.set('preferences', json_prefs)


class AdminForm(FlaskForm):
    organization_logo = FileField(label='Change logo')
    google_sheets_upload = BooleanField(label='Enable upload to Google Sheets')
    enable_nfc = BooleanField(label='Enable NFC')
    enable_printing = BooleanField(label='Enable printing')
    print_logo = BooleanField(label='Include logo with each print')
    print_qr_code = BooleanField(label='Include QR code with each print')
    enable_pronouns = BooleanField(label='Enable pronoun selection')
    spreadsheet_id = StringField(label='Google Sheets Spreadsheet ID')
    text_x_offset_pct = DecimalRangeField(label='Text x position (%)', default=0,
                                          validators=[NumberRange(min=0, max=100)])
    text_y_offset_pct = DecimalRangeField(label='Text y position (%)', default=0,
                                          validators=[NumberRange(min=0, max=100)])
    qr_x_offset_pct = DecimalRangeField(label='QR code x position (%)', default=0,
                                        validators=[NumberRange(min=0, max=100)])
    qr_y_offset_pct = DecimalRangeField(label='QR code y position (%)', default=0,
                                        validators=[NumberRange(min=0, max=100)])
    qr_max_width_pct = DecimalRangeField(label='QR code max width (%)', default=0,
                                         validators=[NumberRange(min=0, max=100)])
    logo_x_offset_pct = DecimalRangeField(label='Logo x position (%)', default=0,
                                          validators=[NumberRange(min=0, max=100)])
    logo_y_offset_pct = DecimalRangeField(label='Logo y position (%)', default=0,
                                          validators=[NumberRange(min=0, max=100)])
    logo_scale = DecimalRangeField(label='Logo scale', default=0)
    thank_you_message = TextAreaField(label='Thank you message', render_kw={"rows": 10, "cols": 30})


@app.route('/render', methods=['POST'])
def render_nametag():
    request_json = request.get_json()
    logger.info('render_nametag request: {}'.format(str(request_json)))
    prefs = get_preferences(r)
    if prefs is None:
        logger.info('No preferences found in Redis')
        return
    nametag = Nametag(text_line1="Swathi Lal",
                      logo_scale=prefs['logo_scale'],
                      logo_x_offset_pct=prefs['logo_x_offset_pct'], logo_y_offset_pct=prefs['logo_y_offset_pct'],
                      qr_max_width_pct=prefs['qr_max_width_pct'],
                      qr_x_offset_pct=prefs['qr_x_offset_pct'], qr_y_offset_pct=prefs['qr_y_offset_pct'],
                      text_x_offset_pct=prefs['text_x_offset_pct'], text_y_offset_pct=prefs['text_y_offset_pct'],
                      # ttf_file="/Library/Fonts/Tahoma.ttf",
                      ttf_file="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                      show_diag=False)

    # return send_file('test.png', mimetype='image/png')
    return jsonify({'nametag': 'data:image/png;charset=utf-8;base64,' + str(nametag.output_as_base64(), "utf-8")})


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        logger.info('form response on submit:')
        for field in request.form:
            logger.info('response< {}:{} ({})'.format(field, str(request.form.get(field, None)), type(field)))
        fields = {
            'google_sheets_upload': bool(request.form.get('google_sheets_upload', None)),
            'enable_printing': bool(request.form.get('enable_printing', None)),
            'print_logo': bool(request.form.get('print_logo', None)),
            'print_qr_code': bool(request.form.get('print_qr_code', None)),
            'enable_nfc': bool(request.form.get('enable_nfc', None)),
            'enable_pronouns': bool(request.form.get('enable_pronouns', None)),
            'thank_you_message': request.form.get('thank_you_message', None),
            'spreadsheet_id': request.form.get('spreadsheet_id', None),
            'text_x_offset_pct': round(float(request.form.get('text_x_offset_pct', None)), 2),
            'text_y_offset_pct': round(float(request.form.get('text_y_offset_pct', None)), 2),
            'qr_x_offset_pct': round(float(request.form.get('qr_x_offset_pct', None)), 2),
            'qr_y_offset_pct': round(float(request.form.get('qr_y_offset_pct', None)), 2),
            'qr_max_width_pct': round(float(request.form.get('qr_max_width_pct', None)), 2),
            'logo_x_offset_pct': round(float(request.form.get('logo_x_offset_pct', None)), 2),
            'logo_y_offset_pct': round(float(request.form.get('logo_y_offset_pct', None)), 2),
            'logo_scale': round(float(request.form.get('logo_scale', None)), 2)
        }
        setPreferences(fields)

    form = AdminForm()
    logger.info('rendering the admin template')
    current_preferences = get_preferences(r)

    if current_preferences is None or all(value is None for value in current_preferences.values()):
        logger.info("Unexpected blank value for preferences")
        # logger.info("Preferences are currently empty; pre-loading with defaults")
        # setPreferences(DEFAULT_PREFERENCES)
        # current_preferences = DEFAULT_PREFERENCES

    for p in current_preferences:
        logger.info("current> {}:{} ({})".format(p, current_preferences[p], type(current_preferences[p])))
    # form.data = current_preferences
    form.google_sheets_upload.data = bool(current_preferences.get('google_sheets_upload'))
    form.enable_nfc.data = bool(current_preferences.get('enable_nfc'))
    form.enable_printing.data = bool(current_preferences.get('enable_printing'))
    form.print_logo.data = bool(current_preferences.get('print_logo'))
    form.print_qr_code.data = bool(current_preferences.get('print_qr_code'))
    form.enable_pronouns.data = bool(current_preferences.get('enable_pronouns'))
    form.thank_you_message.data = current_preferences.get('thank_you_message')
    form.spreadsheet_id.data = current_preferences.get('spreadsheet_id')
    form.text_x_offset_pct.data = float(current_preferences.get('text_x_offset_pct'))
    form.text_y_offset_pct.data = float(current_preferences.get('text_y_offset_pct'))
    form.qr_x_offset_pct.data = float(current_preferences.get('qr_x_offset_pct'))
    form.qr_y_offset_pct.data = float(current_preferences.get('qr_y_offset_pct'))
    form.qr_max_width_pct.data = float(current_preferences.get('qr_max_width_pct'))
    form.logo_x_offset_pct.data = float(current_preferences.get('logo_x_offset_pct'))
    form.logo_y_offset_pct.data = float(current_preferences.get('logo_y_offset_pct'))
    form.logo_scale.data = float(current_preferences.get('logo_scale'))
    for d in form.data:
        logger.info(">>{}:{} ({})".format(d, form.data[d], str(type(form.data[d]))))
    return render_template('admin.html', form=form, preferences=current_preferences)


@app.route('/signin', methods=['POST'])
def signin():
    if request.method == 'POST':
        logger.info("'name = '{}' pronoun = '{}' email = '{}' use_server_img = '{}' nametag_img = '{}'".format(
            str(request.form.get('name', None)),
            str(request.form['pronoun']),
            str(request.form.get('email', None)),
            str(request.form.get('use_server_img', None)),
            str(request.form.get('nametag_img', None))))

        img_file = os.path.join(os.sep, get_script_path(), IMAGE_FILE)
        logger.info("saving temp image at {}".format(img_file))

        use_server_img = bool(request.form.get('use_server_img', False))
        prefs = get_preferences(r)

        with open(img_file, "wb") as f:
            if use_server_img:
                line1 = str(request.form.get('name', None))
                data = Nametag.nametag_from_prefs(line1, '', prefs)
            else:
                # Removing the prefix 'data:image/png;base64,'
                logger.info('image data: {}'.format(request.form['nametag_img']))
                data = request.form['nametag_img'].split(",")[1]

            f.write(base64.b64decode(data))

        if prefs['google_sheets_upload']:
            save_user_info(request.form['name'], request.form['pronoun'], request.form['email'])

        # print only if the submit button value is "print"
        if prefs['enable_printing'] and request.form['button'] == "print":
            logger.info("Printing nametag for \"%s\"" % request.form['name'])
            send_to_printer(img_file)
            return render_template("thankyou.html", message="Your nametag will print soon.")

        # otherwise simply submit
        elif request.form['button'] == "noprint":
            logger.info("Not printing for \"{}\"".format(request.form['name']))
            return render_template("thankyou.html", message="Successfully signed in, enjoy your hack night!")


def start_webserver():
    # server_ip = utils.get_server_ip_address()
    # logger.info("IP: %s"%server_ip)
    app.run(host='0.0.0.0', port=PORT_NUMBER, debug=DEBUG)


if __name__ == "__main__":
    from BadgeHub.log_helper import setup_logging
    setup_logging()
    start_webserver()
