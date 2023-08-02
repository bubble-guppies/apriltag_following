import unittest
import april_tag
import cv2

class TestAprilsTags(unittest.TestCase):

    #ALEX
    def test_get_tags(self):
        self.assertRaises(TypeError, lambda: april_tag.get_tags(None))
        self.assertNotEqual(april_tag.get_tags())
    
    #CHARLOTTE
    def test_PID(self):
        self.assertEquals(april_tag.output_from_tags(), 0, 0)

    #DANIELA
    def test_frames(self):
        pass

    #TOBY
    def test_correct_center_multiple_tags(self):
        img = cv2.imread('test_multi.jpg', cv2.IMREAD_GRAYSCALE)
        self.assertAlmostEquals(april_tag.process_center_avg(img)[0], 22.174)
        self.assertAlmostEquals(april_tag.process_center_avg(img)[0], 5.336)


    def test_position(self):
        img = cv2.imread('testframe.jpg', cv2.IMREAD_GRAYSCALE)
        self.assertEquals(april_tag.process_center_avg(img)[0], -10.1996)
        self.assertNotEquals(april_tag.process_center_avg(img)[1], 5)


img = cv2.imread('test_multi.jpg', cv2.IMREAD_GRAYSCALE)
print(april_tag.process_center_avg(img)[1])

    

