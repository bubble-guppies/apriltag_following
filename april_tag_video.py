from dt_apriltags import Detector
import numpy as np
import cv2
from pid import *
from april_tag import *
import matplotlib.pyplot as plt

def draw_tags(tags: list, img: np.ndarray):
    """Draws a list of tags into the image.
    Args:
        tags (list[tag]): the list of tags to render
        img (_type_): the image to render tags on
    Returns:
        img: the image with tags drawn onto it
    """
    for tag in tags:
        for idx in range(len(tag.corners)):
            cv2.line(
                img,
                tuple(tag.corners[idx - 1, :].astype(int)),
                tuple(tag.corners[idx, :].astype(int)),
                (0, 255, 0),
                thickness=10,
            )
        cv2.line(
            img,
            (int(img.shape[1] / 2), int(img.shape[0] / 2)),
            (int(tag.center[0]), int(tag.center[1])),
            (0, 0, 255),
            thickness=10,
        )

    return img


if __name__ == "__main__":
    cap = cv2.VideoCapture('at_AUV_vid.mkv')
    ret, frame1 = cap.read()
    height, width, layers = frame1.shape
    size = (width, height)
    out = cv2.VideoWriter("rendered_tags.mp4", cv2.VideoWriter_fourcc(*'mp4v'), 30, size)

    count = 0 # the number of frames since the last    
    while ret:
        ret, frame = cap.read()
        if not ret:
            break

        print(f"now on frame {count}...")
        tags = get_tags(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        img = draw_tags(tags, frame)

        out.write(frame)

        count += 1

    cap.release()
    out.release()
    print("Finished rendering the video.")