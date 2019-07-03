import os

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
CSV_FILENAME = os.path.join(os.path.expanduser('~'), "userInformation.csv")
SPREADSHEET_ID = '1e6PV5ejmVUXSXiHPJR033pR1d-wKvLR8G9xWr_n4wtc'
DEBUG = True
PORT_NUMBER = 5000
STATUS_UPDATE_DELAY_SECONDS = 1
PRINT_CHECK_DELAY_SECONDS = 1

DEFAULT_PREFERENCES = {
    'google_sheets_upload': True,
    'enable_printing': True,
    'enable_nfc': False,
    'print_logo': True,
    'print_qr_code': True,
    'enable_pronouns': False,
    'thank_you_message': "Successfully signed in, enjoy your hack night!",
    'spreadsheet_id': '1e6PV5ejmVUXSXiHPJR033pR1d-wKvLR8G9xWr_n4wtc',
    # 'font_file': '/Library/Fonts/Tahoma.ttf',                           # this is for macOS
    'font_file': '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',      # this is for Raspberry Pi
    'text_x_offset_pct': 0.5,
    'text_y_offset_pct': 0.05,
    'qr_x_offset_pct': 0.0,
    'qr_y_offset_pct': 1.0,
    'qr_max_width_pct': 0.20,
    'logo_x_offset_pct': 1.0,
    'logo_y_offset_pct': 1.0,
    'logo_scale': 0.7
}
