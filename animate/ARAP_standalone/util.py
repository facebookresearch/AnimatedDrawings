import os
from PIL import Image, ImageOps
import numpy as np
import OpenGL.GL as GL
import math


def normalized(vector):
    """ normalized version of any vector, with zero division check """
    norm = math.sqrt(sum(vector * vector))
    return vector / norm if norm > 0. else vector

def prep_texture(image, channels):
    image = ImageOps.flip(image)
    imageData = np.array(list(image.getdata()), np.uint8)

    texture_id = GL.glGenTextures(1)
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 4)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_BASE_LEVEL, 0)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAX_LEVEL, 0)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, channels, image.size[0], image.size[1], 0, channels, GL.GL_UNSIGNED_BYTE,
                    imageData)

    image.close()
    return texture_id


def point_in_triangle(pt, v1, v2, v3):

    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    d1 = sign(pt, v1, v2)
    d2 = sign(pt, v2, v3)
    d3 = sign(pt, v3, v1)

    has_neg = d1 < 0 or d2 < 0 or d3 < 0
    has_pos = d1 > 0 or d2 > 0 or d3 > 0

    if not (has_neg and has_pos):
        return True
    else:
        return False


def get_barycentric_coords(p, a, b, c):
    v0 = b - a
    v1 = c - a
    v2 = p - a
    d00 = np.dot(v0, v0)
    d01 = np.dot(v0, v1)
    d11 = np.dot(v1, v1)
    d20 = np.dot(v2, v0)
    d21 = np.dot(v2, v1)
    denom = d00 * d11 - d01 * d01
    v = (d11 * d20 - d01 * d21) / denom
    w = (d00 * d21 - d01 * d20) / denom
    u = 1.0 - v - w

    return u, v, w

