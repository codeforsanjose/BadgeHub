from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import BooleanField, StringField, TextAreaField
from wtforms.fields.html5 import DecimalRangeField
from wtforms.validators import NumberRange

from BadgeHub.models.badge_profile import BadgeProfile


class AdminForm(FlaskForm):
    profile_name = StringField(label='Profile name')
    is_current_profile = BooleanField(label='Default profile')
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

    def populate_fields(self, profile: BadgeProfile):
        self.profile_name.data = profile.profile_name
        self.is_current_profile.data = bool(profile.is_current_profile)
        self.google_sheets_upload.data = bool(profile.google_sheets_upload)
        self.enable_nfc.data = bool(profile.enable_nfc)
        self.enable_printing.data = bool(profile.enable_printing)
        self.print_logo.data = bool(profile.print_logo)
        self.print_qr_code.data = bool(profile.print_qr_code)
        self.enable_pronouns.data = bool(profile.enable_pronouns)
        self.thank_you_message.data = profile.thank_you_message
        self.spreadsheet_id.data = profile.spreadsheet_id
        self.text_x_offset_pct.data = float(profile.text_x_offset_pct)
        self.text_y_offset_pct.data = float(profile.text_y_offset_pct)
        self.qr_x_offset_pct.data = float(profile.qr_x_offset_pct)
        self.qr_y_offset_pct.data = float(profile.qr_y_offset_pct)
        self.qr_max_width_pct.data = float(profile.qr_max_width_pct)
        self.logo_x_offset_pct.data = float(profile.logo_x_offset_pct)
        self.logo_y_offset_pct.data = float(profile.logo_y_offset_pct)
        self.logo_scale.data = float(profile.logo_scale)
