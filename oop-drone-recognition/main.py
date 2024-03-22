import opencv_handler
import onvif_controller

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

HOSTNAME = "192.168.255.108"
PORT = 80
ONVIF_USERNAME = "admin"
ONVIF_PASSWORD = ""

opencv_handler = opencv_handler.OpenCVHandler(stream_source=0,
                                              drone_cascade_path="../models/haarcascade_drone_20.xml",
                                              window_name="OOP Drone Recognition System",
                                              window_width=WINDOW_WIDTH,
                                              window_height=WINDOW_HEIGHT)

onvif_controller = onvif_controller.OnvifController(hostname=HOSTNAME,
                                                    port=PORT,
                                                    username=ONVIF_USERNAME,
                                                    password=ONVIF_PASSWORD)

is_tracking = False
is_following = False


# TODO: multithreading for opencv-python and onvif-python

# KINDA DONE: track when already aimed on
# DONE: generate a possible movement rectangle in the middle while tracking,
#       create isTracking boolean

def main_loop():
    global is_tracking, is_following

    opencv_handler.capture_stream()

    detection_output = opencv_handler.detect_drone_objects()
    if detection_output is not False:
        is_tracking = True
        x_velocity, y_velocity, zoom, is_following = detection_output
        onvif_controller.continuous_move(x_velocity, y_velocity, is_following, zoom)

    if is_tracking is True and detection_output is False:
        is_tracking = False
        onvif_controller.stop_camera()

    opencv_handler.display_frame()

    key = opencv_handler.handle_keystrokes()
    if key == ord("3"):
        onvif_controller.absolute_move()
    elif key == ord('9'):
        onvif_controller.increment_speed()
    elif key == ord('0'):
        onvif_controller.decrement_speed()


if __name__ == "__main__":
    while True:
        main_loop()
