class COCOSkeleton(object):
    
    def __init__(self):
        self.root = 'Neck' # median of left shoulder and right shoulder
        self.keypoint2index = {
            'Nose': 0,
            'LeftEye': 1,
            'RightEye': 2,
            'LeftEar': 3,
            'RightEar': 4,
            'LeftShoulder': 5,
            'RightShoulder': 6,
            'LeftElbow': 7,
            'RightElbow': 8,
            'LeftWrist': 9,
            'RightWrist': 10,
            'LeftHip': 11,
            'RightHip': 12,
            'LeftKnee': 13,
            'RightKnee': 14,
            'LeftAnkle': 15,
            'RightAnkle': 16,
            'Neck': 17
        }
        self.index2keypoint = {v: k for k, v in self.keypoint2index.items()}
        self.keypoint_num = len(self.keypoint2index)

        self.children = {
            'Neck': [
                'Nose', 'LeftShoulder', 'RightShoulder', 'LeftHip', 'RightHip'
            ],
            'Nose': ['LeftEye', 'RightEye'],
            'LeftEye': ['LeftEar'],
            'LeftEar': [],
            'RightEye': ['RightEar'],
            'RightEar': [],
            'LeftShoulder': ['LeftElbow'],
            'LeftElbow': ['LeftWrist'],
            'LeftWrist': [],
            'RightShoulder': ['RightElbow'],
            'RightElbow': ['RightWrist'],
            'RightWrist': [],
            'LeftHip': ['LeftKnee'],
            'LeftKnee': ['LeftAnkle'],
            'LeftAnkle': [],
            'RightHip': ['RightKnee'],
            'RightKnee': ['RightAnkle'],
            'RightAnkle': []
        }
        self.parent = {self.root: None}
        for parent, children in self.children.items():
            for child in children:
                self.parent[child] = parent