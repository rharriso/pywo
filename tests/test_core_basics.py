import unittest

import os
import sys
sys.path.insert(0, '../')
sys.path.insert(0, './')


from core import Gravity, Size, Geometry, Borders

class TestSize(unittest.TestCase):

    def setUp(self):
        self.HALF_FULL = Size(0.5, 1.0)

    def test_parse(self):
        self.assertEqual(Size.parse('', ''), None)
        self.assertEqual(Size.parse('', 'FULL'), None)
        self.assertEqual(Size.parse('HALF', ''), None)
        self.assertEqual(Size.parse('HALF', 'FULL'), self.HALF_FULL)
        self.assertEqual(Size.parse('HALF', '1'), self.HALF_FULL)
        self.assertEqual(Size.parse('HALF', '1.0'), self.HALF_FULL)
        self.assertEqual(Size.parse('HALF', 'HALF*2'), self.HALF_FULL)
        self.assertEqual(Size.parse('HALF', 'QUARTER*2+HALF'), self.HALF_FULL)
        self.assertEqual(Size.parse('1.0/2', '0.1*6-0.1+HALF'), self.HALF_FULL)
        self.assertEqual(Size.parse('HALF, FULL', '1'), Size([0.5, 1], 1))


class TestGravity(unittest.TestCase):

    def setUp(self):
        self.TOP = Gravity(0.5, 0)
        self.BOTTOM = Gravity(0.5, 1)
        self.RIGHT = Gravity(1, 0.5)
        self.LEFT = Gravity(0, 0.5)
        self.MIDDLE = Gravity(0.5, 0.5)
        self.TOP_LEFT = Gravity(0, 0)
        self.BOTTOM_RIGHT = Gravity(1, 1)
        self.TOP_RIGHT = Gravity(1, 0)
        self.BOTTOM_LEFT = Gravity(0, 1)

    def test_equal(self):
        self.assertEqual(Gravity(1, 0), self.TOP_RIGHT)
        self.assertEqual(Gravity(1.0, 0.0), self.TOP_RIGHT)
        self.assertEqual(Gravity(0.5, 0.5), self.MIDDLE)

    def test_is_direction(self):
        self.assert_(self.TOP.is_top)
        self.assert_(not self.TOP.is_bottom)
        self.assert_(not self.TOP.is_left)
        self.assert_(not self.TOP.is_right)
        self.assert_(not self.TOP.is_middle)
        self.assert_(not self.BOTTOM_LEFT.is_top)
        self.assert_(not self.BOTTOM_LEFT.is_right)
        self.assert_(self.BOTTOM_LEFT.is_bottom)
        self.assert_(self.BOTTOM_LEFT.is_left)
        self.assert_(not self.BOTTOM_LEFT.is_middle)
        self.assert_(self.MIDDLE.is_middle)

    def test_invert(self):
        self.assertNotEqual(self.TOP.invert(), self.TOP)
        self.assertEqual(self.TOP.invert(), self.BOTTOM)
        self.assertNotEqual(self.LEFT.invert(), self.LEFT)
        self.assertEqual(self.LEFT.invert(), self.RIGHT)
        self.assertEqual(self.BOTTOM_LEFT.invert(), self.TOP_RIGHT)
        self.assertEqual(self.MIDDLE.invert(), self.MIDDLE)
        self.assertEqual(self.BOTTOM_LEFT.invert(vertical=False), self.BOTTOM_RIGHT)
        self.assertEqual(self.BOTTOM_LEFT.invert(horizontal=False), self.TOP_LEFT)

    def test_parse(self):
        self.assertEqual(Gravity.parse('TOP'), self.TOP)
        self.assertEqual(Gravity.parse('UP'), self.TOP)
        self.assertEqual(Gravity.parse('FULL, 0'), self.TOP_RIGHT)
        self.assertEqual(Gravity.parse('FULL, 0.0'), self.TOP_RIGHT)
        self.assertEqual(Gravity.parse('1, 0'), self.TOP_RIGHT)
        self.assertEqual(Gravity.parse('1,0'), self.TOP_RIGHT)
        self.assertEqual(Gravity.parse('1.0, 0.0'), self.TOP_RIGHT)
        self.assertEqual(Gravity.parse('1.0,0.0'), self.TOP_RIGHT)
        self.assertEqual(Gravity.parse('HALF, HALF'), self.MIDDLE)
        self.assertEqual(Gravity.parse('HALF, 0.5'), self.MIDDLE)
        self.assertEqual(Gravity.parse('HALF, 1.0/2'), self.MIDDLE)
        self.assertEqual(Gravity.parse('0.5, 1.0-0.5'), self.MIDDLE)
        self.assertEqual(Gravity.parse('0.25*2, 2.0/2-0.5'), self.MIDDLE)
        self.assertEqual(Gravity.parse('QUARTER*2, FULL/2'), self.MIDDLE)
        self.assertRaises(ValueError, Gravity.parse, 'top')
        self.assertRaises(ValueError, Gravity.parse, 'slkfsk')
        self.assertRaises(ValueError, Gravity.parse, '1.0')
        self.assertRaises(ValueError, Gravity.parse, '1,2,3')


class TestGeometry(unittest.TestCase):
    
    def test_constructor(self):
        geo = Geometry(100, 150, 20, 30)
        self.assertEquals(geo.x2, 120)
        self.assertEquals(geo.y2, 180)
        geo = Geometry(100, 150, 20, 30, Gravity(1, 1))
        self.assertEquals(geo.x2, 100)
        self.assertEquals(geo.y2, 150)
        self.assertEquals(geo.x, 80)
        self.assertEquals(geo.y, 120)
        geo = Geometry(1.1, 2.9, 10.5, 15.2)
        self.assertEquals(geo.x, 1)
        self.assertEquals(geo.y, 2)
        self.assertEquals(geo.width, 10)
        self.assertEquals(geo.height, 15)

    def test_set_position(self):
        geo = Geometry(0, 0, 100, 200)
        self.assertEquals(geo.x, 0)
        self.assertEquals(geo.y, 0)
        geo.set_position(10, 10)
        self.assertEquals(geo.x, 10)
        self.assertEquals(geo.y, 10)
        geo.set_position(110, 210, Gravity(1, 1))
        self.assertEquals(geo.x, 10)
        self.assertEquals(geo.y, 10)
        geo.set_position(60, 110, Gravity(0.5, 0.5))
        self.assertEquals(geo.x, 10)
        self.assertEquals(geo.y, 10)


class TestBorders(unittest.TestCase):

    def test_vertical_horizontal(self):
        borders = Borders(10, 20, 17, 13)
        self.assertEquals(borders.horizontal, 30)
        self.assertEquals(borders.vertical, 30)


if __name__ == '__main__':
    main_suite = unittest.TestSuite()
    for suite in [TestSize, TestGravity, TestGeometry, TestBorders]:
        main_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(suite))
    unittest.TextTestRunner(verbosity=2).run(main_suite)
