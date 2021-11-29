import cv2 as cv
import numpy as np

vid = cv.VideoWriter('pyout1.mp4', cv.VideoWriter_fourcc(*'x264'), 25, (300,300))
#vid = cv.VideoWriter('pyout.mp4', 0x00000021, 25, (300,300))

for i in range(250):
    img = np.random.randint(0,255, (300,300,3), dtype=np.uint8)
    vid.write(img)
vid.release()
