from threading import Thread, Event
from time import sleep
import numpy as np
from pid import PID
from video import Video
from bluerov_interface import BlueROV
from pymavlink import mavutil

# TODO: import your processing functions
from april_tag import *

# Create the video object
video = Video()
# Create the PID object
PIDVertical = PID(0.09,0,0,100)
PIDHorizontal = PID(0.05,0,0,100)
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
    global new_frame
    global vertical_power
    global horizontal_power
    
    while not video.frame_available():
        print("Waiting for frame...")
        sleep(0.01)

    try:
        while True:
            if video.frame_available():
                frame = video.frame()
                # TODO: Add frame processing here
                if type(frame) == np.ndarray:
                    vertical_power, horizontal_power = process_frame(frame, PIDVertical=PIDVertical, PIDHorizontal=PIDHorizontal)
                
                # TODO: set vertical_power and lateral_power here
                _send_rc()
                print(frame.shape)
    except KeyboardInterrupt:
        return


def _send_rc():
    bluerov.set_vertical_power(vertical_power)
    bluerov.set_lateral_power(lateral_power)


def main():
    # Start the video thread
    video_thread = Thread(target=_get_frame)
    video_thread.start()

    # Start the RC thread
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
