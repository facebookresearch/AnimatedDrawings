import logging
from collections import defaultdict
from pathlib import Path
from typing import Union
import yaml
from pkg_resources import resource_filename

from animated_drawings.utils import resolve_ad_filepath


class Config():

    def __init__(self, user_mvc_cfg_fn: str) -> None:
        # get the base mvc config
        with open(resource_filename(__name__, "mvc_base_cfg.yaml"), 'r') as f:
            base_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader) or {})  # pyright: ignore[reportUnknownMemberType])

        # search for the user-specified mvc confing
        user_mvc_cfg_p: Path = resolve_ad_filepath(user_mvc_cfg_fn, 'user mvc config')
        logging.info(f'Using user-specified mvc config file located at {user_mvc_cfg_p.resolve()}')
        with open(str(user_mvc_cfg_p), 'r') as f:
            user_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader) or {})  # pyright: ignore[reportUnknownMemberType]

        # overlay user specified mvc options onto base mvc, use to generate subconfig classes
        self.scene: SceneConfig = SceneConfig({**base_cfg['scene'], **user_cfg['scene']})
        self.view: ViewConfig = ViewConfig({**base_cfg['view'], **user_cfg['view']})
        self.controller: ControllerConfig = ControllerConfig({**base_cfg['controller'], **user_cfg['controller']})

        # check if video render controller, then output video path and codec cannot be none


class SceneConfig():

    def __init__(self, scene_cfg: dict) -> None:  # type: ignore

        # show or hide the floor
        self.add_floor: bool = scene_cfg['ADD_FLOOR']
        try:
            assert isinstance(self.add_floor, bool), 'is not bool'
        except AssertionError as e:
            msg = f'Error in ADD_FLOOR config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # show or hide visualization of BVH motion driving characters
        self.add_ad_retarget_bvh: bool = scene_cfg['ADD_AD_RETARGET_BVH']
        try:
            assert isinstance(self.add_ad_retarget_bvh, bool), 'is not bool'
        except AssertionError as e:
            msg = f'Error in ADD_AD_RETARGET_BVH config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # config files for characters, driving motions, and retargeting
        self.animated_characters: list[dict[str, str]] = scene_cfg['ANIMATED_CHARACTERS']
        try:
            for dict_ in self.animated_characters:
                assert 'character_cfg' in dict_.keys(), 'missing character_cfg'
                assert 'motion_cfg' in dict_.keys(), 'missing motion_cfg'
                assert 'retarget_cfg' in dict_.keys(), 'missing retarget_cfg'
        except AssertionError as e:
            msg = f'Error in ANIMATED_CHARACTERS config parameter: {e}'
            logging.critical(msg)
            assert False, msg


class ViewConfig():

    def __init__(self, view_cfg: dict) -> None:  # type: ignore

        # set color used to clear render buffer
        self.clear_color: list[Union[float, int]] = view_cfg["CLEAR_COLOR"]
        try:
            assert len(self.clear_color) == 4, 'length not four'
            for val in self.clear_color:
                assert isinstance(val, (float, int)), f'{val} not float or int'
                assert val <= 1.0, 'values must be <= 1.0'
                assert val >= 0.0, 'values must be >= 0.0'
        except AssertionError as e:
            msg = f'Error in CLEAR_COLOR config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set an image to use for the background, if desired
        self.background_image: Union[None, str] = view_cfg["BACKGROUND_IMAGE"]
        try:
            assert isinstance(self.background_image, (NoneType, str)), 'type not NoneType or str'
        except AssertionError as e:
            msg = f'Error in BACKGROUND_IMAGE config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set the dimensions of the window or output video
        self.window_dimensions: tuple[int, int] = view_cfg["WINDOW_DIMENSIONS"]
        try:
            assert len(self.window_dimensions) == 2, 'length is not 2'
            for val in self.window_dimensions:
                assert val > 0, f'{val} must be > 0'
                assert isinstance(val, int), 'type not int'
        except AssertionError as e:
            msg = f'Error in WINDOW_DIMENSIONS config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set whether we want the character rigs to be visible
        self.draw_ad_rig: bool = view_cfg['DRAW_AD_RIG']
        try:
            assert isinstance(self.draw_ad_rig, bool), 'value is not bool type'
        except AssertionError as e:
            msg = f'Error in DRAW_AD_RIG config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set whether we want the character textures to be visible
        self.draw_ad_txtr: bool = view_cfg['DRAW_AD_TXTR']
        try:
            assert isinstance(self.draw_ad_txtr, bool), 'value is not bool type'
        except AssertionError as e:
            msg = f'Error in DRAW_AD_TXTR config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set whether we want the character triangle->bone assignment colors to be visible
        self.draw_ad_color: bool = view_cfg['DRAW_AD_COLOR']
        try:
            assert isinstance(self.draw_ad_color, bool), 'value is not bool type'
        except AssertionError as e:
            msg = f'Error in DRAW_AD_COLOR config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set whether we want the character mesh lines to be visible
        self.draw_ad_mesh_lines: bool = view_cfg['DRAW_AD_MESH_LINES']
        try:
            assert isinstance(self.draw_ad_mesh_lines, bool), 'value is not bool type'
        except AssertionError as e:
            msg = f'Error in DRAW_AD_MESH_LINES config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set whether we want to use mesa on the back end (necessary for headless rendering)
        self.use_mesa: bool = view_cfg['USE_MESA']
        try:
            assert isinstance(self.use_mesa, bool), 'value is not bool type'
        except AssertionError as e:
            msg = f'Error in USE_MESA config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set the position of the view camera
        self.camera_pos: list[Union[float, int]] = view_cfg['CAMERA_POS']
        try:
            assert len(self.camera_pos) == 3, 'length != 3'
            for val in self.camera_pos:
                assert isinstance(val, (float, int)), f' {val} is not float or int'
        except AssertionError as e:
            msg = f'Error in CAMERA_POS config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set the forward vector of the view camera (but it renders out of it's rear)
        self.camera_fwd: list[Union[float, int]] = view_cfg['CAMERA_FWD']
        try:
            assert len(self.camera_fwd) == 3, 'length != 3'
            for val in self.camera_fwd:
                assert isinstance(val, (float, int)), f' {val} is not float or int'
        except AssertionError as e:
            msg = f'Error in CAMERA_FWD config parameter: {e}'
            logging.critical(msg)
            assert False, msg


class ControllerConfig():

    def __init__(self, controller_cfg: dict) -> None:  # type: ignore

        # set controller mode
        self.mode: str = controller_cfg["MODE"]
        try:
            assert isinstance(self.mode, str), 'is not str'
            assert self.mode in ('interactive', 'video_render'), 'mode not interactive or video_render'
        except AssertionError as e:
            msg = f'Error in MODE config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set timestep for user interactions in interactive mode
        self.keyboard_timestep: Union[float, int] = controller_cfg["KEYBOARD_TIMESTEP"]
        try:
            assert isinstance(self.keyboard_timestep, (float, int)), 'is not floar or int'
            assert self.keyboard_timestep > 0, 'timestep val must be > 0'
        except AssertionError as e:
            msg = f'Error in KEYBOARD_TIMESTEP config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set output video path (only use in video_render mode)
        self.output_video_path: Union[None, str] = controller_cfg['OUTPUT_VIDEO_PATH']
        try:
            assert isinstance(self.output_video_path, (NoneType, str)), 'type is not None or str'
            if isinstance(self.output_video_path, str):
                assert Path(self.output_video_path).suffix in ('.gif', '.mp4'), 'output video extension not .gif or .mp4 '
        except AssertionError as e:
            msg = f'Error in OUTPUT_VIDEO_PATH config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set output video codec (only use in video_render mode with .mp4)
        self.output_video_codec: Union[None, str] = controller_cfg['OUTPUT_VIDEO_CODEC']
        try:
            assert isinstance(self.output_video_codec, (NoneType, str)), 'type is not None or str'
        except AssertionError as e:
            msg = f'Error in OUTPUT_VIDEO_CODEC config parameter: {e}'
            logging.critical(msg)
            assert False, msg


class MotionConfig():

    def __init__(self) -> None:
        pass


class RetargetConfig():

    def __init__(self) -> None:
        pass


NoneType = type(None)  # needed for type checking
