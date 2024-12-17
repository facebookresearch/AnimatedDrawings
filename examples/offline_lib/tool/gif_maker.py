'''
Ussage of this script:
    python gif_maker.py --vid_path <your video complete path> --gif_path <your output gif complete path>
'''
import imageio
import cv2
import os.path as osp
import os
import glob


def get_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--vid_path', default='./demo.mp4', help='src video path')
    parser.add_argument('--gif_path', default='out.gif', help='target gif output path')
    args = parser.parse_args()
    return args


def convert_video_2_gif(src_video_path: str, output_save_path: str):
    '''
    convert *.mp4 -> *.gif
    '''
    video_reader = cv2.VideoCapture(src_video_path)
    fps = int(video_reader.get(cv2.CAP_PROP_FPS))
    frame_list = []
    print('Start Convert Gif!!')
    while True:
        ret, frame = video_reader.read()
        if ret is False:
            break

        frame = frame[..., ::-1]
        frame_list.append(frame)

    imageio.mimsave(output_save_path, frame_list, 'GIF', duration=1 / fps * 1000, loop=0)
    print('Gif Has Convert Done!!')


if __name__ == '__main__':
    args = get_args()
    video_path = args.vid_path
    gif_name = args.gif_path
    convert_video_2_gif(src_video_path=video_path, output_save_path=gif_name)
