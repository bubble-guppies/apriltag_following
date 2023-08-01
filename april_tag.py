from dt_apriltags import Detector
import numpy as np
import cv2
from pid import *

cameraMatrix = np.array([1060.71, 0, 960, 0, 1060.71, 540, 0, 0, 1]).reshape((3, 3))

camera_params = (
    cameraMatrix[0, 0],
    cameraMatrix[1, 1],
    cameraMatrix[0, 2],
    cameraMatrix[1, 2],
)
at_detector = Detector(
    families="tag36h11",
    nthreads=1,
    quad_decimate=1.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0,
)

def get_tags(img) -> list:
    """Gets a list of tags from an image.

    Args:
        img: the image, in grayscale

    Returns:
        list: the list of tags found in the image
    """
    if type(img) is not np.ndarray:
        raise TypeError("img parameter is of incorrect type.")

    tags = at_detector.detect(img, True, camera_params=camera_params, tag_size=True)

    if type(tags) is not None:
        print("tag found!")
    
    return tags


def get_positions(tags: list) -> list[tuple[float, float, int]]:
    """A representation of the tag using only the pixel coordinates.

    Args:
        tags (list): the list of tags to process

    Returns:
        list[tuple[float, float, int]]: the list of tags, each defined as [x, y, tag_id]
    """
    return [[tag.center[0], tag.center[1], tag.tag_id] for tag in tags]


def error_relative_to_center(
    centers: list[tuple[float, float, int]], width: int, height: int
) -> list[tuple[float, float, int]]:
    """The error relative to the center of the image. Used for PID.

    Args:
        centers (list[tuple[float, float, int]]): the list of tags, typically the output of get_positions
        width (int): the width of the image
        height (int): the height of the image

    Returns:
        list[tuple[float, float, int]]: the list of error values for each tag
    """
    x_center = height / 2
    y_center = width / 2
    return [
        [0.5*center[0] - 0.5*x_center, 0.5*y_center - 0.5*center[1], center[2]] for center in centers
    ]


def output_from_tags(errors, horizontal_pid: PID, vertical_pid: PID) -> tuple[list[float], list[float]]:
    if len(errors) == 0:
        horizontal_output = 0
        vertical_output = 0
    else:
        horizontal_output = [horizontal_pid.update(error[0]) for error in errors]
        vertical_output = [vertical_pid.update(error[1]) for error in errors]
    return (horizontal_output, vertical_output)

def draw_outputs(img, outputs: tuple[list[float], list[float]], tags):
    h_off_center = 25
    v_off_center = 50
    for i in range(len(outputs) - 1):
        tag = tags[i]
        horizontal = outputs[0][i]
        vertical = outputs[1][i]
        cv2.putText(
            img,
            f"Horizontal: {horizontal:.2f}%",
            org=(int(img.shape[1]/2) + h_off_center, int(img.shape[0]/2) + v_off_center),
            fontFace=cv2.FONT_HERSHEY_TRIPLEX,
            fontScale=1.5,
            color=(0, 0, 255),
        )
        cv2.putText(
            img,
            f"Vertical: {vertical:.2f}%",
            org=(int(img.shape[1]/2) + h_off_center, int(img.shape[0]/2)),
            fontFace=cv2.FONT_HERSHEY_TRIPLEX,
            fontScale=1.5,
            color=(0, 0, 255),
        )
    return img


def render_tags(tags, img):
    """Renders a list of tags into the image.

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
        cv2.line(img, (int(img.shape[1]/2), int(img.shape[0]/2)), (int(tag.center[0]), int(tag.center[1])), (0, 0, 255), thickness=10)

    return img

def process_frame(frame, PIDHorizontal, PIDVertical):
    powY = 0
    powX = 0
    apriltags = get_tags(frame)
    if len(apriltags) > 0:
        centers = get_positions(apriltags)
        relative_centers = error_relative_to_center(centers, frame.shape[0], frame.shape[1])
        cv2.imwrite("testframe.jpg", frame)
        
        x = [center[1] for center in relative_centers]
        y = [center[0] for center in relative_centers]
        meanY = np.mean(y)
        meanX = np.mean(x)

        powY = PIDHorizontal.update(meanY)
        powX = PIDVertical.update(meanX)

    return (powX, powY)

def process_center_avg(frame):
    apriltags = get_tags(frame)
    if len(apriltags) > 0:
        centers = get_positions(apriltags)
        relative_centers = error_relative_to_center(centers, frame.shape[0], frame.shape[1])     
        x = [center[1] for center in relative_centers]
        y = [center[0] for center in relative_centers]


        meanY = np.mean(y)
        meanX = np.mean(x)


    return (meanX, meanY)