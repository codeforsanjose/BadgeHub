import unittest

from modules.image_creator import Nametag


class ImageCreatorTests(unittest.TestCase):

    def test_pos_0_pct(self):
        obj_x, obj_y = Nametag.position_inside_boundaries(obj_offset=(0.0, 0.0), obj_size=(100, 100),
                                                  canvas_size=(1000, 1000), margin_px=0)
        self.assertEqual(0, obj_x)
        self.assertEqual(0, obj_y)

    def test_pos_50_pct(self):
        obj_x, obj_y = Nametag.position_inside_boundaries(obj_offset=(0.5, 0.5), obj_size=(100, 100),
                                                  canvas_size=(1000, 1000), margin_px=0)
        self.assertEqual(450, obj_x)
        self.assertEqual(450, obj_y)

    def test_pos_100_pct(self):
        obj_x, obj_y = Nametag.position_inside_boundaries(obj_offset=(1.0, 1.0), obj_size=(100, 100),
                                                  canvas_size=(1000, 1000), margin_px=0)
        self.assertEqual(900, obj_x)
        self.assertEqual(900, obj_y)


if __name__ == '__main__':
    unittest.main()
