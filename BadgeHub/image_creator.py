import base64
import logging
import math
from io import BytesIO

import qrcode
from PIL import Image, ImageDraw, ImageFont

from BadgeHub.models.badge_profile import BadgeProfile

PRINT_DPI = 300
PAGE_WIDTH_IN = 4.0
PAGE_HEIGHT_IN = 2.25
PAGE_WIDTH_PX = math.floor(PAGE_WIDTH_IN * PRINT_DPI)
PAGE_HEIGHT_PX = math.floor(PAGE_HEIGHT_IN * PRINT_DPI)

logger = logging.getLogger(__name__)


class Nametag:
    def __init__(self, text_line1: str, text_line2: str = None,
                 width: int = PAGE_WIDTH_PX, height: int = PAGE_HEIGHT_PX,
                 margin_pct: float = 0.05,
                 logo_src: str = None, logo_scale: float = 1.0,
                 logo_x_offset_pct: float = 0, logo_y_offset_pct: float = 0,
                 qr_x_offset_pct: float = 0, qr_y_offset_pct: float = 0, qr_max_width_pct: float = 1,
                 text_x_offset_pct: float = 0, text_y_offset_pct: float = 0,
                 ttf_file: str = None, show_diag: bool = False) -> None:
        logger.info("using width={}, height={}".format(width, height))
        self.im = Image.new('RGBA', (width, height), color=None)
        self.height = height
        self.width = width
        self.margin_pct = margin_pct
        self.margin_px = math.floor(max(self.width, self.height) * self.margin_pct)

        self.logo_src = logo_src
        self.logo_scale = logo_scale
        self.logo_x_offset_pct = logo_x_offset_pct
        if 0 > self.logo_x_offset_pct > 1.0:
            logger.info('logo_x_offset_pct should be in the range [0,1]')
            self.logo_x_offset_pct = self.margin_pct
        self.logo_y_offset_pct = logo_y_offset_pct
        if 0 > self.logo_y_offset_pct > 1.0:
            logger.info('logo_y_offset_pct should be in the range [0,1]')
            self.logo_y_offset_pct = self.margin_pct

        self.qr_x_offset_pct = qr_x_offset_pct
        self.qr_y_offset_pct = qr_y_offset_pct
        self.qr_max_width_pct = qr_max_width_pct
        if 0 > self.qr_x_offset_pct > 1.0:
            logger.info('qr_x_offset_pct should be in the range [0,1]')
            self.qr_x_offset_pct = self.margin_pct
        if 0 > self.qr_y_offset_pct > 1.0:
            logger.info('qr_y_offset_pct should be in the range [0,1]')
            self.qr_y_offset_pct = self.margin_pct

        self.text_line1 = text_line1
        self.text_line2 = text_line2
        self.text_x_offset_pct = text_x_offset_pct
        if 0 > self.text_x_offset_pct > 1.0:
            logger.info('text_x_offset_pct should be in the range [0,1]')
            self.text_x_offset_pct = self.margin_pct
        self.text_y_offset_pct = text_y_offset_pct
        if 0 > self.text_y_offset_pct > 1.0:
            logger.info('text_y_offset_pct should be in the range [0,1]')
            self.text_y_offset_pct = self.margin_pct
        self.ttf_file = ttf_file
        self.show_diag = show_diag
        self.draw()

    def update_text(self, text):
        self.text_line1 = text
        self.draw()

    def draw(self):
        self.draw_logo()
        self.draw_text()
        self.draw_qr()
        self.draw_diag_lines()

    def save(self, filepath='test.png', format='PNG'):
        logger.info('saving image with dimensions: [{}, {}]'.format(self.width, self.height))
        self.im.save(filepath, format)

    def output_as_base64(self):
        buffered = BytesIO()
        self.im.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())

    def draw_text(self):
        draw = ImageDraw.Draw(self.im)
        font_size = math.floor(PAGE_HEIGHT_PX / 6)
        while True:
            font_size = font_size - 1
            font = ImageFont.truetype(self.ttf_file, font_size)
            size_x, size_y = draw.textsize(self.text_line1, font=font)
            if size_x < (self.width - self.margin_px * 2):
                break
        pos_x, pos_y = self.position_inside_boundaries(obj_offset=(self.text_x_offset_pct, self.text_y_offset_pct),
                                                       obj_size=(size_x, size_y), canvas_size=(self.width, self.height),
                                                       margin_px=self.margin_px)
        draw.text((pos_x, pos_y), self.text_line1, font=font, fill='Black')
        logger.info(
            'font size={}, text size=({}, {}), text pos=({}, {})'.format(font_size, size_x, size_y, pos_x, pos_y))

    def draw_logo(self):
        logo_im = Image.open("static/images/organization_logo.jpg").convert('LA')
        logo_im.thumbnail((logo_im.size[0] * self.logo_scale, logo_im.size[1] * self.logo_scale), Image.ANTIALIAS)
        pos_x, pos_y = self.position_inside_boundaries(obj_offset=(self.logo_x_offset_pct, self.logo_y_offset_pct),
                                                       obj_size=logo_im.size, canvas_size=(self.width, self.height),
                                                       margin_px=self.margin_px)
        self.im.paste(logo_im, (pos_x, pos_y))

    def draw_qr(self):
        qr_max_width_px = self.qr_max_width_pct * self.width
        qr_box_size = 2
        while True:
            qr_box_size = qr_box_size + 1
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=qr_box_size
            )
            qr.add_data(self.text_line1)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            if qr_img.size[0] > qr_max_width_px:
                break
        qr_pos_x, qr_pos_y = self.position_inside_boundaries(obj_offset=(self.qr_x_offset_pct, self.qr_y_offset_pct),
                                                             obj_size=qr_img.size,
                                                             canvas_size=(self.width, self.height),
                                                             margin_px=self.margin_px)
        logger.info("QR code width={}, height={}, pos=({}, {})"
                     .format(qr_img.size[0], qr_img.size[1], qr_pos_x, qr_pos_y))
        self.im.paste(qr_img, (qr_pos_x, qr_pos_y))

    def draw_diag_lines(self):
        if self.show_diag:
            draw = ImageDraw.Draw(self.im)
            # center
            center_color = (255, 0, 0, 150)
            draw.line((self.width / 2, 0, self.width / 2, self.height), fill=center_color, width=1)
            draw.line((0, self.height / 2, self.width, self.height / 2), fill=center_color, width=1)
            # margins
            margin_color = (0, 255, 0, 150)
            draw.line((0, self.margin_px, self.width, self.margin_px), fill=margin_color, width=1)
            draw.line((0, self.height - self.margin_px, self.width, self.height - self.margin_px),
                      fill=margin_color, width=1)
            draw.line((self.margin_px, 0, self.margin_px, self.height), fill=margin_color, width=1)
            draw.line((self.width - self.margin_px, 0, self.width - self.margin_px, self.height),
                      fill=margin_color, width=1)

    @staticmethod
    def position_inside_boundaries(obj_offset: tuple, obj_size: tuple, canvas_size: tuple, margin_px: int):
        # keep the object inside the bounds of the image, considering the margins as well.
        usable_space = {'w': canvas_size[0] - (2 * margin_px), 'h': canvas_size[1] - (2 * margin_px)}
        obj_center = {'w': math.floor(obj_size[0] * obj_offset[0]), 'h': math.floor(obj_size[1] * obj_offset[1])}
        return [math.floor(margin_px + ((obj_offset[0] * usable_space['w']) - obj_center['w'])),
                math.floor(margin_px + ((obj_offset[1] * usable_space['h']) - obj_center['h']))]

    @staticmethod
    def nametag_from_profile(text_line1: str, text_line2: str, profile: BadgeProfile):
        nt = Nametag(text_line1=text_line1,
                     text_line2=text_line2,
                     logo_scale=profile.logo_scale,
                     logo_x_offset_pct=profile.logo_x_offset_pct,
                     logo_y_offset_pct=profile.logo_y_offset_pct,
                     qr_max_width_pct=profile.qr_max_width_pct,
                     qr_x_offset_pct=profile.qr_x_offset_pct,
                     qr_y_offset_pct=profile.qr_y_offset_pct,
                     text_x_offset_pct=profile.text_x_offset_pct,
                     text_y_offset_pct=profile.text_y_offset_pct,
                     ttf_file=profile.font_file,
                     show_diag=False)
        return nt.output_as_base64()


# # TODO: allow font selection using python-fclist
# # https://github.com/MonsieurV/python-fclist
#
# for font in fclist(fontformat='TrueType'):
#     print(font.family, font.style, font.file)
# font = ImageFont.truetype("/Library/Fonts/Tahoma.ttf", math.floor(PAGE_HEIGHT_PX / 6))
if __name__ == '__main__':
    from .log_helper import setup_logging

    setup_logging()
    from .config import DEFAULT_PREFERENCES

    nametag = Nametag(text_line1="Test User",
                      text_line2="someone@example.com",
                      logo_scale=DEFAULT_PREFERENCES['logo_scale'],
                      logo_x_offset_pct=DEFAULT_PREFERENCES['logo_x_offset_pct'],
                      logo_y_offset_pct=DEFAULT_PREFERENCES['logo_y_offset_pct'],
                      qr_max_width_pct=DEFAULT_PREFERENCES['qr_max_width_pct'],
                      qr_x_offset_pct=DEFAULT_PREFERENCES['qr_x_offset_pct'],
                      qr_y_offset_pct=DEFAULT_PREFERENCES['qr_y_offset_pct'],
                      text_x_offset_pct=DEFAULT_PREFERENCES['text_x_offset_pct'],
                      text_y_offset_pct=DEFAULT_PREFERENCES['text_y_offset_pct'],
                      ttf_file=DEFAULT_PREFERENCES['font_file'],
                      show_diag=True)
    nametag.save()
