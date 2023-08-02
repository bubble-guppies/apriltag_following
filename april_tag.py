from dt_apriltags import Detector
import numpy as np
import cv2
from pid import *
import eigency


# Create an April Tags detector object
cameraMatrix = np.array([ 353.571428571, 0, 320, 0, 353.571428571, 180, 0, 0, 1]).reshape((3,3))

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

    tags = at_detector.detect(img, True, camera_params=camera_params, tag_size=0.1)

    if len(tags) > 0:
        print("tag(s) found!")

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
        [(center[0] - x_center)/x_center, (y_center - center[1])/y_center, center[2]]
        for center in centers
    ]




def pid_from_frame(frame: np.ndarray, PIDHorizontal: PID, PIDVertical: PID):
    """Processes a frame to find the PID power output.

    Args:
        frame (np.ndarray): the image
        PIDHorizontal (PID): the horizontal PID controller
        PIDVertical (PID): the vertical PID controller

    Returns:
        tuple[float, float]: the vertical and horizontal PID outputs
    """
    powY = 0
    powX = 0
    apriltags = get_tags(frame)
    if len(apriltags) > 0:
        meanX, meanY = process_center_avg(frame)

        powY = PIDHorizontal.update(meanY)
        powX = PIDVertical.update(meanX)

    return (powX, powY)


def process_center_avg(frame: np.ndarray) -> tuple[float, float]:
    """Given a frame, finds the tags and

    Args:
        frame (np.ndarray): an image that may contain april tags

    Returns:
        tuple[float, float]: the centroid of all of the april tags found in the image, or (width/2, height/2) if none are found
    """
    meanX = frame.shape[1]/2 # default values
    meanY = frame.shape[0]/2

    apriltags = get_tags(frame)
    if len(apriltags) > 0:
        centers = get_positions(apriltags)
        relative_centers = error_relative_to_center(
            centers, frame.shape[0], frame.shape[1]
        )

        x = [center[1] for center in relative_centers]
        y = [center[0] for center in relative_centers]

        meanY = np.mean(y)
        meanX = np.mean(x)

    return (meanX, meanY)


def get_heading_to_tag(frame):
    apriltags = get_tags(frame)
    print(apriltags)
    rot = apriltags[0].pose_R
    r = rotation_matrix_to_euler_angles(rot)
    return r


def rotation_matrix_to_euler_angles(rot_matrix):
    # Ensure the input is a 3x3 rotation matrix
    if rot_matrix.shape != (3, 3):
        raise ValueError("Input matrix must be a 3x3 rotation matrix.")

    # Calculate pitch (around y-axis) and yaw (around z-axis)
    pitch = np.arcsin(-rot_matrix[2, 0])
    yaw = np.arctan2(rot_matrix[1, 0], rot_matrix[0, 0])

    # Calculate roll (around x-axis)
    cos_pitch = np.cos(pitch)
    if np.abs(cos_pitch) > 1e-6:
        roll = np.arctan2(rot_matrix[2, 1] / cos_pitch, rot_matrix[2, 2] / cos_pitch)
    else:
        # Gimbal lock case: cos(pitch) is close to zero
        roll = 0.0

    # Convert angles from radians to degrees
    roll_deg = np.degrees(roll)
    pitch_deg = np.degrees(pitch)
    yaw_deg = np.degrees(yaw)
    print(f"{(180/np.pi)*roll_deg, (180/np.pi)*pitch_deg, (180/np.pi)*yaw_deg}")
    return yaw_deg


def get_distance_to_tag(frame):
    apriltags = get_tags(frame)
    dist = [tag.pose_t[2] for tag in apriltags]
    print(apriltags)
    meanY = np.mean(dist)
    return meanY