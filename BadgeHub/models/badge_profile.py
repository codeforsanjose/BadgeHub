import json

from BadgeHub.utils import convert_to_dict

# FIXME: this class is messy and error-prone, should use a map or something that ties the string representation to the fields.

class BadgeProfile:

    def __init__(self, profile_id: int = 1,
                 profile_name: str = "Default Profile",
                 is_current_profile: bool = False,
                 google_sheets_upload: bool = True,
                 enable_printing: bool = True,
                 enable_nfc: bool = False,
                 print_logo: bool = True,
                 print_qr_code: bool = False,
                 enable_pronouns: bool = False,
                 thank_you_message: str or None = "Successfully signed in, enjoy your hack night!",
                 spreadsheet_id: str or None = None,
                 font_file: str = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',  # this is for Raspberry Pi
                 text_x_offset_pct: float = 0.5,
                 text_y_offset_pct: float = 0.05,
                 qr_x_offset_pct: float = 0.0,
                 qr_y_offset_pct: float = 1.0,
                 qr_max_width_pct: float = 0.20,
                 logo_x_offset_pct: float = 1.0,
                 logo_y_offset_pct: float = 1.0,
                 logo_scale: float = 0.7):
        self.profile_id: int = profile_id
        self.profile_name: str = profile_name
        self.is_current_profile: bool = is_current_profile
        self.google_sheets_upload: bool = google_sheets_upload
        self.enable_printing: bool = enable_printing
        self.enable_nfc: bool = enable_nfc
        self.print_logo: bool = print_logo
        self.print_qr_code: bool = print_qr_code
        self.enable_pronouns: bool = enable_pronouns
        self.thank_you_message: str or None = thank_you_message
        self.spreadsheet_id: str or None = spreadsheet_id
        self.font_file: str or None = font_file
        self.text_x_offset_pct: float = text_x_offset_pct
        self.text_y_offset_pct: float = text_y_offset_pct
        self.qr_x_offset_pct: float = qr_x_offset_pct
        self.qr_y_offset_pct: float = qr_y_offset_pct
        self.qr_max_width_pct: float = qr_max_width_pct
        self.logo_x_offset_pct: float = logo_x_offset_pct
        self.logo_y_offset_pct: float = logo_y_offset_pct
        self.logo_scale: float = logo_scale

    @staticmethod
    def from_dict(di):
        # TODO
        p = BadgeProfile.from_form(di)
        p.profile_id = int(di['profile_id'])
        return p


    @staticmethod
    def from_form(form: dict):
        profile = BadgeProfile()
        profile.profile_name = form.get('profile_name', None)
        profile.is_current_profile = bool(form.get('is_current_profile', None))
        profile.google_sheets_upload = bool(form.get('google_sheets_upload', None))
        profile.enable_printing = bool(form.get('enable_printing', None))
        profile.print_logo = bool(form.get('print_logo', None))
        profile.print_qr_code = bool(form.get('print_qr_code', None))
        profile.enable_nfc = bool(form.get('enable_nfc', None))
        profile.enable_pronouns = bool(form.get('enable_pronouns', None))
        profile.thank_you_message = form.get('thank_you_message', None)
        profile.spreadsheet_id = form.get('spreadsheet_id', None)
        profile.text_x_offset_pct = round(float(form.get('text_x_offset_pct', None)), 2)
        profile.text_y_offset_pct = round(float(form.get('text_y_offset_pct', None)), 2)
        profile.qr_x_offset_pct = round(float(form.get('qr_x_offset_pct', None)), 2)
        profile.qr_y_offset_pct = round(float(form.get('qr_y_offset_pct', None)), 2)
        profile.qr_max_width_pct = round(float(form.get('qr_max_width_pct', None)), 2)
        profile.logo_x_offset_pct = round(float(form.get('logo_x_offset_pct', None)), 2)
        profile.logo_y_offset_pct = round(float(form.get('logo_y_offset_pct', None)), 2)
        profile.logo_scale = round(float(form.get('logo_scale', None)), 2)
        return profile

    def to_json(self):
        return json.dumps(self, sort_keys=True, default=convert_to_dict)