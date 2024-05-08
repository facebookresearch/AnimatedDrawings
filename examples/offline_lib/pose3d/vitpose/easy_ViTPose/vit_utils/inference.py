import cv2
import numpy as np
import json


rotation_map = {
    0: None,
    90: cv2.ROTATE_90_COUNTERCLOCKWISE,
    180: cv2.ROTATE_180,
    270: cv2.ROTATE_90_CLOCKWISE
}

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def draw_bboxes(image, bounding_boxes, boxes_id, scores):
    image_with_boxes = image.copy()

    for bbox, bbox_id, score in zip(bounding_boxes, boxes_id, scores):
        x1, y1, x2, y2 = bbox
        cv2.rectangle(image_with_boxes, (x1, y1), (x2, y2), (128, 128, 0), 2)

        label = f'#{bbox_id}: {score:.2f}'

        (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        label_x = x1
        label_y = y1 - 5 if y1 > 20 else y1 + 20

        # Draw a filled rectangle as the background for the label
        cv2.rectangle(image_with_boxes, (x1, label_y - label_height - 5),
                      (x1 + label_width, label_y + 5), (128, 128, 0), cv2.FILLED)
        cv2.putText(image_with_boxes, label, (label_x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    return image_with_boxes


def pad_image(image: np.ndarray, aspect_ratio: float) -> np.ndarray:
    # Get the current aspect ratio of the image
    image_height, image_width = image.shape[:2]
    current_aspect_ratio = image_width / image_height

    left_pad = 0
    top_pad = 0
    # Determine whether to pad horizontally or vertically
    if current_aspect_ratio < aspect_ratio:
        # Pad horizontally
        target_width = int(aspect_ratio * image_height)
        pad_width = target_width - image_width
        left_pad = pad_width // 2
        right_pad = pad_width - left_pad

        padded_image = np.pad(image,
                              pad_width=((0, 0), (left_pad, right_pad), (0, 0)),
                              mode='constant')
    else:
        # Pad vertically
        target_height = int(image_width / aspect_ratio)
        pad_height = target_height - image_height
        top_pad = pad_height // 2
        bottom_pad = pad_height - top_pad

        padded_image = np.pad(image,
                              pad_width=((top_pad, bottom_pad), (0, 0), (0, 0)),
                              mode='constant')
    return padded_image, (left_pad, top_pad)


class VideoReader(object):
    def __init__(self, file_name, rotate=0):
        self.file_name = file_name
        self.rotate = rotation_map[rotate]
        try:  # OpenCV needs int to read from webcam
            self.file_name = int(file_name)
        except ValueError:
            pass

    def __iter__(self):
        self.cap = cv2.VideoCapture(self.file_name)
        if not self.cap.isOpened():
            raise IOError('Video {} cannot be opened'.format(self.file_name))
        return self

    def __next__(self):
        was_read, img = self.cap.read()
        if not was_read:
            raise StopIteration
        if self.rotate is not None:
            img = cv2.rotate(img, self.rotate)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
