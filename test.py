import os
import cv2
import april_tag
import numpy as np

img = cv2.imread('testframe.jpg', cv2.IMREAD_GRAYSCALE)
folder = "./"
output_path = os.path.join(folder, f"img.jpg")
print(april_tag.get_heading_to_tag(img) * (180/np.pi))


        

