import time
from Shapes.BVH import BVH


class TimeManager:

    def __init__(self, cfg):  # mode='INTERACT', render_fps=None):
        assert cfg['RENDER_MODE'] in ['INTERACT', 'RENDER']
        self.mode = cfg['RENDER_MODE']

        if self.mode == 'RENDER':
            assert cfg['RENDER_FPS'] is not None
        self.render_fps = cfg['RENDER_FPS']

        self.cur_scene_frame = None  # current frame within the scene
        self.cur_bvh_frame = None    # current frame within the BVH

        self.loop_count = 0  # keep track of times the BVH file has been looped

        self.is_playing = None

        self.spf = None  # seconds per frame of the bvh

        self.scene_time = None  # time through scene, in seconds
        self.scene_last_time = None

        self.bvh_time = None  # time through the current clip, in seconds

        self.render_last_time = None  # keeps track of how many seconds since last render loop
        self.fps = None
        self.last_fps_time = None

        self.bvh = None

        self.step_size = 1

    def get_fps(self):
        if self.mode == 'INTERACT':
            if self.render_last_time is None:
                self.render_last_time = time.time()
                self.last_fps_time = time.time()
                self.fps = -1.0
                return self.fps
            else:
                tmp = time.time()
                if tmp - self.last_fps_time > 0.5:
                    self.last_fps_time = time.time()
                    self.fps = 1 / (tmp - self.render_last_time)
                self.render_last_time = tmp
                return self.fps
        else:  # self.mode == 'RENDER'
            return self.render_fps

    def initialize_time(self):
        self.scene_last_time = time.time()
        self.scene_time = self.bvh_time = 0.0

    def initialize_bvh(self, bvh: BVH):
        self.bvh = bvh

        self.cur_scene_frame = self.cur_bvh_frame = 0

        self.spf = bvh.frametime

        self.is_playing = False

    def toggle_play(self):
        if self.is_playing:
            self.bvh_time = self.cur_bvh_frame * self.spf
            self.scene_time = self.cur_scene_frame * self.spf
            self.is_playing = False
        else:
            self.is_playing = True
            self.scene_last_time = time.time()

    def _tick_interact(self):
        if not self.is_playing:  # if we're not playing
            return

        next_time = time.time()  # get the time
        time_step = next_time - self.scene_last_time
        self.bvh_time += time_step
        self.scene_time += time_step

        self.scene_last_time = next_time

        frame_step = int(time_step / self.spf)  # take the bvh_time (in seconds) divided by seconds per frame to get the frame

        self.cur_scene_frame = self.cur_scene_frame + frame_step
        self.cur_bvh_frame += frame_step

        if self.cur_bvh_frame >= self.bvh.frame_count:
            self.loop_count += 1
            self.cur_bvh_frame = self.cur_scene_frame % self.bvh.frame_count

    def _tick_render(self):
        frame_step = int(1 / (self.render_fps * self.spf))

        self.cur_scene_frame += frame_step

        self.cur_bvh_frame += frame_step
        if self.cur_bvh_frame >= self.bvh.frame_count:
            self.loop_count += 1
            self.cur_bvh_frame = self.cur_scene_frame % self.bvh.frame_count

    def tick(self):
        if self.mode == 'INTERACT':
            self._tick_interact()
        else:  # self.mode == 'RENDER'
            self._tick_render()

    def set_inc_dec_step_size(self, step_size: int):
        self.step_size = step_size

    def increment_frame(self):
        self.bvh_time = self.bvh_time + (self.step_size * self.spf)

        self.cur_scene_frame = int(self.bvh_time / self.spf)
        self.cur_bvh_frame = self.cur_scene_frame % self.bvh.frame_count

    def decrement_frame(self):
        self.bvh_time = self.bvh_time - (self.step_size * self.spf)

        self.cur_scene_frame = int(self.bvh_time / self.spf)
        self.cur_bvh_frame = self.cur_scene_frame % self.bvh.frame_count

        # self.cur_frame -= self.step_size
        # self.cur_frame %= self.bvh.frame_count

        # self.bvh_time = self.cur_frame * self.spf

    def get_current_bvh_frame(self):
        return self.cur_bvh_frame
