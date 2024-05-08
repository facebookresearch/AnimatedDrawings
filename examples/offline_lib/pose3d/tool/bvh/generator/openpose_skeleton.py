class OpenPoseSkeleton(object):

    def __init__(self):
        self.root = 'MidHip'
        self.keypoint2index = {
            'Nose': 0,
            'Neck': 1,
            'RShoulder': 2,
            'RElbow': 3,
            'RWrist': 4,
            'LShoulder': 5,
            'LElbow': 6,
            'LWrist': 7,
            'MidHip': 8,
            'RHip': 9,
            'RKnee': 10,
            'RAnkle': 11,
            'LHip': 12,
            'LKnee': 13,
            'LAnkle': 14,
            'REye': 15,
            'LEye': 16,
            'REar': 17,
            'LEar': 18,
            'LBigToe': 19,
            'LSmallToe': 20,
            'LHeel': 21,
            'RBigToe': 22,
            'RSmallToe': 23,
            'RHeel': 24
        }
        self.index2keypoint = {v: k for k, v in self.keypoint2index.items()}
        self.keypoint_num = len(self.keypoint2index)

        self.children = {
            'MidHip': ['Neck', 'RHip', 'LHip'],
            'Neck': ['Nose', 'RShoulder', 'LShoulder'],
            'Nose': ['REye', 'LEye'],
            'REye': ['REar'],
            'REar': [],
            'LEye': ['LEar'],
            'LEar': [],
            'RShoulder': ['RElbow'],
            'RElbow': ['RWrist'],
            'RWrist': [],
            'LShoulder': ['LElbow'],
            'LElbow': ['LWrist'],
            'LWrist': [],
            'RHip': ['RKnee'],
            'RKnee': ['RAnkle'],
            'RAnkle': ['RBigToe', 'RSmallToe', 'RHeel'],
            'RBigToe': [],
            'RSmallToe': [],
            'RHeel': [],
            'LHip': ['LKnee'],
            'LKnee': ['LAnkle'],
            'LAnkle': ['LBigToe', 'LSmallToe', 'LHeel'],
            'LBigToe': [],
            'LSmallToe': [],
            'LHeel': [],
        }
        self.parent = {self.root: None}
        for parent, children in self.children.items():
            for child in children:
                self.parent[child] = parent