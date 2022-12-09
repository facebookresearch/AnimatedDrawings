import time
from sketch_animate.Shapes.BVH import BVH


class TimeManager:

    def __init__(self, cfg):  # mode='INTERACT', render_fps=None):
        self.cur_scene_frame = 0        # current frame within the scene
        self.cur_bvh_frame = 0          # current frame within the BVH
        self.loop_count = 0             # keep track of times the BVH file has been looped
        self.is_playing = None
        self.spf = None                 # seconds per frame of the bvh
        self.scene_time = None          # time through scene, in seconds
        self.scene_last_time = None
        self.bvh_time = None            # time through the current clip, in seconds
        self.render_last_time = None    # keeps track of how many seconds since last render loop
        self.fps = None
        self.last_fps_time = None
        self.bvh = None
        self.step_size = 1

    def get_fps(self):
        raise NotImplementedError("TimeManager subclass must implement method: get_fps")

    def initialize_time(self):
        self.scene_last_time = time.time()
        self.scene_time = self.bvh_time = 0.0

    def tick(self):
        raise NotImplementedError("TimeManager subclass must implement method: tick")

    def get_current_bvh_frame(self):
        return self.cur_bvh_frame


class TimeManager_Render(TimeManager):

    def __init__(self, cfg):
        super().__init__(cfg)

        self.bvh_frame_count = None

    def get_fps(self):
        return 30  # always render at 30 FPS

    def set_bvh_frame_count(self, val):
        self.bvh_frame_count = val

    def tick(self):
        frame_step = 1

        self.cur_scene_frame += frame_step
        self.cur_bvh_frame += frame_step

        if self.cur_bvh_frame >= self.bvh_frame_count:
            self.loop_count += 1
            self.cur_bvh_frame = self.cur_scene_frame % self.bvh_frame_count


class TimeManager_Interact(TimeManager):

    def __init__(self, cfg):
        super().__init__(cfg)
        self.render_fps = cfg['RENDER_FPS']

    def get_fps(self):
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

    def initialize_bvh(self, bvh: BVH):
        self.bvh = bvh
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

    def tick(self):
        if not self.is_playing:
            return

        next_time = time.time()
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
