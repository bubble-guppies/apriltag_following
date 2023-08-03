import os
import cv2
import april_tag
import numpy as np

img = cv2.imread('./tobytestimg/3.jpg', cv2.IMREAD_GRAYSCALE)
print(april_tag.get_heading_to_tag(img))


        

    