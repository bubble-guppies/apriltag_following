from threading import Thread, Event
from time import sleep
import numpy as np
from pid import PID
from video import Video
from bluerov_interface import BlueROV
from pymavlink import mavutil

# TODO: import your processing functions
from april_tag import *

print("Main started!")

# Create the video object
video = Video()
# Create the PID object
PIDVertical = PID(50,0,0,100)
PIDHorizontal = PID(50,0,0,100)
# Create the mavlink connection
mav_comn = mavutil.mavlink_connection("udpin:0.0.0.0:14550")
# Create the BlueROV object
bluerov = BlueROV(mav_connection=mav_comn)

frame = None
frame_available = Event()
frame_available.set()

vertical_power = 0
lateral_power = 0


def _get_frame():
    global frame
    global vertical_power
    global lateral_power
    
    while not video.frame_available():
        print("Waiting for frame...")
        sleep(0.01)

    try:
        while True:
            if video.frame_available():
                frame = video.frame()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # TODO: Add frame processing here
                if type(frame) == np.ndarray:
                    try:
                        vertical_power, lateral_power = pid_from_frame(frame, PIDVertical=PIDVertical, PIDHorizontal=PIDHorizontal)
                        print(f"{vertical_power = }")
                        print(f"{lateral_power = }")
                    except Exception as e:
                        print(f"caught: {e}")
                
                # TODO: set vertical_power and lateral_power here
                print(frame.shape)
    except KeyboardInterrupt:
        return


def _send_rc():
    while True:
        bluerov.arm()
        bluerov.set_vertical_power(vertical_power)
        bluerov.set_lateral_power(lateral_power)
        sleep(0.2)


def main():
    # Start the video thread
    video_thread = Thread(target=_get_frame)
    video_thread.start()

    # # Start the RC thread
    rc_thread = Thread(target=_send_rc)
    rc_thread.start()

    # Main loop
    try:
        while True:
            mav_comn.wait_heartbeat()
    except KeyboardInterrupt:
        video_thread.join()
        rc_thread.join()
        bluerov.disarm()
        print("Exiting...")

if __name__ == "__main__":
    main()
