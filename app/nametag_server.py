import base64
import configparser
import csv
import json
import datetime
import logging
import os

# from werkzeug.utils import secure_filename
# from nfc import getBoardInfo
from flask import Flask, request, render_template, jsonify, redirect, url_for


from BadgeHub.config import CSV_FILENAME, DEBUG, PORT_NUMBER
from BadgeHub.image_creator import Nametag
from BadgeHub.models.admin_form import AdminForm
from BadgeHub.models.badge_profile import BadgeProfile
from BadgeHub.redis_helper import redis_instance, get_preferences, get_next_profile_id, get_default_profile, get_preferences_for_id, set_profile, get_printer_status, get_nfc_status, peek_nfc_queue
from BadgeHub.utils import get_script_path
from BadgeHub.printer_manager import send_to_printer

IMAGE_FILE = "temp.png"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


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
    current_preferences = get_default_profile(redis_instance())

    if current_preferences is None or all(value is None for value in current_preferences):
        logger.warning("Unexpected blank value for preferences")

    return render_template('index.html', preferences=current_preferences)


@app.route('/render', methods=['POST'])
def render_nametag():
    request_json = request.get_json()
    logger.info('render_nametag request: {}'.format(str(request_json)))
    default_profile = get_default_profile(redis_instance())

    if default_profile is None:
        logger.error('No dfault profile found in Redis')
        return
    nametag = Nametag(text_line1="Swathi Lal",
                      logo_scale=default_profile.logo_scale,
                      logo_x_offset_pct=default_profile.logo_x_offset_pct, logo_y_offset_pct=default_profile.logo_y_offset_pct,
                      qr_max_width_pct=default_profile.qr_max_width_pct,
                      qr_x_offset_pct=default_profile.qr_x_offset_pct, qr_y_offset_pct=default_profile.qr_y_offset_pct,
                      text_x_offset_pct=default_profile.text_x_offset_pct, text_y_offset_pct=default_profile.text_y_offset_pct,
                      # ttf_file="/Library/Fonts/Tahoma.ttf",
                      ttf_file="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                      show_diag=False)

    # return send_file('test.png', mimetype='image/png')
    return jsonify({'nametag': 'data:image/png;charset=utf-8;base64,' + str(nametag.output_as_base64(), "utf-8")})


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    current_preferences = get_preferences(redis_instance())
    # prefs = json.dumps(current_preferences, sort_keys=True, default=convert_to_dict)

    # if there are no profiles, then create a default one.
    if current_preferences is None or len(current_preferences) == 0:
        default_profile = BadgeProfile()
        profile_id = get_next_profile_id(redis_instance())
        default_profile.profile_id = profile_id
        default_profile.is_current_profile = True
        current_preferences[profile_id] = default_profile
        set_profile(redis_instance(), default_profile)

    return render_template('admin.html', preferences=current_preferences)


@app.route('/admin/status', methods=['GET'])
def get_info():
    info = {
        'printers': get_printer_status(redis_instance()),
        'nfc': get_nfc_status(redis_instance()),
        'cards_pending' : peek_nfc_queue(redis_instance())
        }
    return jsonify(info)


@app.route('/admin/profile/new', methods=['GET'])
def new_profile():
    new_profile = BadgeProfile()
    profile_id = get_next_profile_id(redis_instance())
    new_profile.profile_id = profile_id
    set_profile(redis_instance(), new_profile)
    print(f'creating new profile with ID {profile_id}')
    return redirect(url_for('edit_profile', profile_id=profile_id))


@app.route('/admin/edit/<int:profile_id>', methods=['GET', 'POST'])
def edit_profile(profile_id:int):
    print(f'loading profile ID {profile_id}')
    if request.method == 'POST':
        logger.info('form response on submit:')
        for field in request.form:
            logger.info('response< {}:{} ({})'.format(field, str(request.form.get(field, None)), type(field)))
        profile_from_form_data = BadgeProfile.from_form(request.form)

        # ensures that the profile we're editing corresponds to the URL.
        profile_from_form_data.profile_id = profile_id
        set_profile(redis_instance(), profile_from_form_data)

    form = AdminForm()
    logger.info('rendering the admin template')
    profile = get_preferences_for_id(redis_instance(), profile_id)
    if profile is None:
        return render_template('404.html', title='404'), 404

    # if profile is None or all(value is None for value in profile):
    #     logger.info("Unexpected blank value for preferences")
    #     # logger.info("Preferences are currently empty; pre-loading with defaults")
    #     # setPreferences(DEFAULT_PREFERENCES)
    #     # profile = DEFAULT_PREFERENCES
    
    # for p in profile:
    #     logger.info("current> {}:{} ({})".format(p, profile[p], type(profile[p])))
    # # form.data = profile

    logger.info(f"current> {profile.to_json()}")
  
    form.populate_fields(profile)
    for d in form.data:
        logger.info(">>{}:{} ({})".format(d, form.data[d], str(type(form.data[d]))))
    return render_template('profile_edit.html', form=form, preferences=profile)


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

        default_profile = get_default_profile(redis_instance())

        with open(img_file, "wb") as f:
            if use_server_img:
                line1 = str(request.form.get('name', None))
                data = Nametag.nametag_from_profile(line1, '', default_profile)
            else:
                # Removing the prefix 'data:image/png;base64,'
                logger.info('image data: {}'.format(request.form['nametag_img']))
                data = request.form['nametag_img'].split(",")[1]

            f.write(base64.b64decode(data))

        if default_profile.google_sheets_upload:
            save_user_info(request.form['name'], request.form['pronoun'], request.form['email'])

        # print only if the submit button value is "print"
        if default_profile.enable_printing and request.form['button'] == "print":
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
