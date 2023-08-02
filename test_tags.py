import unittest
import pid
import main
import april_tag

class TestAprilsTags(unittest.TestCase):

    # alex
    def test_get_tags(self):
        # can only get two for now, will add more in class
        self.assertRaises(TypeError, lambda: april_tag.get_tags(None)) # check if type error is raised 
        self.assertEqual(april_tag.get_tags('no_tag.png'), None) # check if using an image with no tags returns the right stuff
    
    #CHARLOTTE
    def test_PID(self):
        self.assertEquals(april_tag.output_from_tags(), 0, 0)

    # idk
    def test_frames(self):
        '''
        make sure you get the right amount of frames and width/size 
        for a frame in a video, maybe make a 30 frame test case
        '''
        pass

    #TOBY
    def test_correct_center_multiple_tags(self):
        self.assertAlmostEquals(april_tag.get_)

