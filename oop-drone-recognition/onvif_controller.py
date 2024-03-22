from typing import Tuple, Dict

from onvif import ONVIFCamera
import numpy as np


class OnvifController:
    def __init__(self, hostname: str, port: int, username: str, password: str) -> None:
        self.camera = ONVIFCamera(hostname, port, user=username, passwd=password)
        print("ONVIFController: Connected to the camera.")

        self.ptz = self.camera.create_ptz_service()
        self.media = self.camera.create_media_service()

        self.media_profile = self.media.GetProfiles()[0]

        self.continuous_move_request = self.ptz.create_type("ContinuousMove")
        self.absolute_move_request = self.ptz.create_type('AbsoluteMove')
        self.relative_move_request = self.ptz.create_type('RelativeMove')

        self.continuous_move_request.ProfileToken = self.media_profile.token
        self.absolute_move_request.ProfileToken = self.media_profile.token
        self.relative_move_request.ProfileToken = self.media_profile.token

        self.continuous_move_request.Velocity = self.ptz.GetStatus({"ProfileToken": self.media_profile.token}).Position

        self.pan_speed_multiplier = 0.5
        print('Default pan speed multiplier: 0.5')

    def increment_speed(self) -> None:
        self.pan_speed_multiplier = np.round(self.pan_speed_multiplier + 0.1, 1)
        print(f'ONVIF: Pan speed multiplier: {self.pan_speed_multiplier}')

    def decrement_speed(self) -> None:
        self.pan_speed_multiplier = np.round(self.pan_speed_multiplier - 0.1, 1)
        print(f'ONVIF: Pan speed multiplier: {self.pan_speed_multiplier}')

    def get_status(self) -> Dict[str, float]:
        status = self.ptz.GetStatus(self.media_profile.token)
        return dict(x=status.Position.PanTilt.x, y=status.Position.PanTilt.y, zoom=status.Position.Zoom.x)

    def continuous_move(self, x_velocity: float, y_velocity: float, is_following: bool, zoom: float = 0) -> None:
        fixed_multiplier = (self.pan_speed_multiplier if is_following is False else 2)

        self.continuous_move_request.Velocity.PanTilt.x = x_velocity * fixed_multiplier
        self.continuous_move_request.Velocity.PanTilt.y = y_velocity * fixed_multiplier
        self.continuous_move_request.Velocity.Zoom.x = 0

        # curr_zoom = self.get_status()['zoom']
        # zoom_diff = zoom - curr_zoom
        # print(f'curr_zoom: {curr_zoom}, desired zoom: {zoom} zoom_diff: {zoom_diff}')

        # self.relative_move(zoom=zoom_diff)
        self.ptz.ContinuousMove(self.continuous_move_request)

    def relative_move(self, x_translation: float = 0, y_translation: float = 0, zoom: float = 0) -> None:
        self.relative_move_request.Translation = {
            'PanTilt': {
                'x': x_translation,
                'y': y_translation
            },
            'Zoom': {
                'x': zoom
            }
        }

        self.ptz.RelativeMove(self.relative_move_request)

    def absolute_move(self, x: int = .5, y: int = .5, zoom: int = 0) -> None:
        self.absolute_move_request.Position = {
            'PanTilt': {
                'x': x,
                'y': y
            },
            'Zoom': {
                'x': zoom
            }
        }

        self.ptz.AbsoluteMove(self.absolute_move_request)

    def stop_camera(self) -> None:
        stop_request = self.ptz.create_type('Stop')
        stop_request.ProfileToken = self.media_profile.token

        self.ptz.Stop(stop_request)
