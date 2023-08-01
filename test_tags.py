import unittest
import pid
import main
import april_tag

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
        self.assertAlmostEquals(april_tag.get_)

