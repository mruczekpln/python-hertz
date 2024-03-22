import cv2 as cv
import time

import numpy
import numpy as np
from typing import Tuple


class OpenCVHandler:
    def __init__(
            self,
            stream_source: str | int,
            drone_cascade_path: str,
            window_name: str,
            window_width: int = 640,
            window_height: int = 480,
    ) -> None:
        self.frame = None
        self.window_name = window_name
        self.window_width = window_width
        self.window_height = window_height

        self.can_display_stats = False
        self.can_display_casts = False

        self.frame_start = 0
        self.average_frametime = []

        # TEMP
        self.zoom_list = []
        self.prev_zoom_list = []

        self.droneCascadeClassifier = cv.CascadeClassifier(drone_cascade_path)
        print("OPENCV: CascadeClassifier init.")

        self.capture = cv.VideoCapture(stream_source)
        print("OPENCV: VideoCapture init.")

    def draw_tracking_area(self) -> None:
        cv.rectangle(self.frame, pt1=(self.window_width // 2 - 100, self.window_height // 2 - 50),
                     pt2=(self.window_width // 2 + 100, self.window_height // 2 + 50), color=(0, 255, 0), thickness=1)

    def evaluate_movement_axes(self, x_distance_from_center: int, y_distance_from_center: int) -> Tuple[float, float]:
        x_velocity = np.round(x_distance_from_center / (self.window_width / 2), 2)
        y_velocity = np.round(y_distance_from_center / (self.window_height / 2), 2) * -1

        return x_velocity, y_velocity

    def draw_drone_indicator(self, x: int, y: int, w: int, h: int) -> None:
        cv.rectangle(self.frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
        cv.putText(
            self.frame,
            "drone",
            (x, y - 10),
            cv.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

    def detect_drone_objects(self) -> bool | Tuple[float, float, float, bool]:
        following = False

        gray_frame = cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)
        gray_frame = cv.equalizeHist(gray_frame)

        drone_objects = self.droneCascadeClassifier.detectMultiScale(image=gray_frame, minNeighbors=7)
        if len(drone_objects) > 0:
            x, y, w, h = drone_objects[0]

            x_target_center = x + w // 2
            y_target_center = y + h // 2

            x_distance_from_center = x_target_center - self.window_width // 2
            y_distance_from_center = y_target_center - self.window_height // 2

            x_velocity, y_velocity = self.evaluate_movement_axes(x_distance_from_center, y_distance_from_center)
            self.zoom_list.append(numpy.round(1 / (w / 15), 1))
            if len(self.zoom_list) == 5:
                self.prev_zoom_list = self.zoom_list
                self.zoom_list = []

                zoom_velocity = 0

                print(f'last_zoom: {self.last_zoom}, zoom: {self.zoom}, zoom_velocity: {zoom_velocity}')

            self.draw_drone_indicator(*drone_objects[0])
            if abs(x_distance_from_center) <= 100 and abs(y_distance_from_center) <= 50:
                self.draw_tracking_area()
                following = True

            return x_velocity, y_velocity, zoom_velocity, following

        return False

    def display_stats(self) -> None:
        frame_end = time.time()

        frametime = np.round(frame_end - self.frame_start, 5)
        self.average_frametime.append(frametime)
        if len(self.average_frametime) > 10:
            self.average_frametime = self.average_frametime[1:11]
        fps = 1 / frametime

        frametime_text = "Frametime: {:.4f} s".format(frametime)
        average_frametime_text = "Average frametime: {:.4f} s".format(np.mean(self.average_frametime))

        cv.putText(self.frame, frametime_text, (0, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv.putText(self.frame, average_frametime_text, (0, 40), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv.putText(self.frame, f"FPS: {int(fps)}", (0, 60), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    def capture_stream(self):
        _, self.frame = self.capture.read()
        if self.frame is None:
            print("ERROR: No frames from camera!")

        self.frame_start = time.time()

    def display_frame(self) -> None:
        if self.can_display_stats:
            self.display_stats()

        cv.imshow(self.window_name, self.frame)

    def handle_keystrokes(self) -> int | None:
        key = cv.waitKey(1) & 0xFF

        if key == ord("q"):
            self.capture.release()
            cv.destroyWindow(self.window_name)
            exit(0)
        elif key == ord("1"):
            self.can_display_stats = not self.can_display_stats
            print(f'can_display_stats: {self.can_display_stats}')

        return key
