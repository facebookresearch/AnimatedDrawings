import argparse
import os
import os.path as osp
import sys
import cv2
from typing import Dict, List
import numpy as np
import numpy.typing as npt
import yaml
import onnxruntime as ort
from collections import OrderedDict
import copy


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--detector_path', type=str, default='detection/deployment/output/sketch_detector.onnx')
    parser.add_argument('--estimator_path', type=str,
                        default='keypoint_estimation/deployment/output/sketch_estimator.onnx')
    parser.add_argument('--img_path', type=str, default='keypoint_estimation/deployment/data/test1.png')
    parser.add_argument('--mor_ite', type=int, default=5,
                        help='Iteration for dialation and close operation when acquire mask.')
    args = parser.parse_args()
    return args


######################################################################################################
# sketch detector
SKETCH_CLASS_INDEX = 0


class SketchDetector():
    single_threshold = 0.2
    nms_threshold = 0.3

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.session = ort.InferenceSession(model_path)
        self.output_tesnor_names = [node.name for node in self.session.get_outputs()]
        self.input_tensor_names = self.session.get_inputs()

    def preprocess(self, img_data):
        '''

        Args:
            img_data: [H,W,C]

        Returns:
            img_tensor: [N=1,C,H,W] with Normalize and ToTensor()
        '''
        norm_mean = [103.53, 116.28, 123.675]
        norm_std = [1.0, 1.0, 1.0]
        to_rgb = False
        img_tensor = cv2.cvtColor(img_data, cv2.COLOR_BGR2RGB)

        # pad to mod by 32 for both width and height
        h, w = img_tensor.shape[:2]
        h, w = [int((_ * 1.5) // 32 * 32) for _ in [h, w]]
        h, w = min(1344, h), min(1344, w)
        # normalize
        img_tensor = (img_tensor - norm_mean) / norm_std
        # [H,W,C] -> [C,H,W]
        img_tensor = np.transpose(img_tensor, (2, 0, 1)).astype(np.float32)

        # For mmdet MaskRCNN, this operation doesn't support
        # data = data.astype(np.float32) / 255.0
        img_tensor = np.expand_dims(img_tensor, axis=0)
        return img_tensor

    def inference(self, img_path, show_res=False):
        '''

        Args:
            img_path: str, path for image
            show_res: bool, if True, the result will be drawn with initial image data.

        Returns:
            combine_res: [ dict{
                              bbox: [x1,y1,x2,y2],
                              mask: [H,W], numpy.array in binary and gray
                            }
                      ]
            Attention: The results have sorted by NMS algorithms through scores of bboxes. The higher the first.
        '''
        assert osp.exists(img_path), 'Image path should exist!!'
        self.img_path = img_path
        img_data = cv2.imread(img_path)
        self.img_data = img_data
        img_tensor = self.preprocess(img_data)
        detector_results = self.session.run(self.output_tesnor_names,
                                            input_feed={self.input_tensor_names[0].name: img_tensor})

        bbox_list, label_list, mask_list = detector_results[0][0], detector_results[1][0], detector_results[2][0]

        combined_res_list = self.postprocess(img_data, bbox_list, label_list, mask_list, show_res=show_res)
        return combined_res_list

    def postprocess(self, img_data, bboxes_list, labels_list, masks_list, show_res: bool = False):
        '''

        Args:
            img_data: [H,W,C]
            bboxes_list: [num_det,5=(x1,y1,x2,y2,score)]
            labels_list: [num_det]
            masks_list: [num_det,H,W]
            show_res: bool, default False. If True, will show results for masks and detected rectangles.

        Returns:
            combined_res: [ dict{
                              bbox: [x1,y1,x2,y2],
                              mask: [H,W], numpy.array in binary and gray
                            }
                      ]
        '''
        # single filter with merely calss and threshold constraint
        single_filtered_bboxes_list, single_filtered_labels_list, single_filtered_masks_list = self._single_thresh_filter(
            bboxes_list, labels_list, masks_list,
            score_thr=SketchDetector.single_threshold)

        single_filtered_scores_list = single_filtered_bboxes_list[:, -1].reshape(-1)
        single_filtered_bboxes_list = single_filtered_bboxes_list[:, :-1]

        # nms filter
        nms_indicies = self._nms(single_filtered_bboxes_list, single_filtered_scores_list, iou_threshold=0.3)

        nms_filtered_bboxes, nms_filtered_masks, nms_filtered_labels = single_filtered_bboxes_list[nms_indicies], \
                                                                       single_filtered_masks_list[nms_indicies], \
                                                                       single_filtered_labels_list[nms_indicies]

        if show_res:
            self.vis_result(img_data, nms_filtered_bboxes, nms_filtered_masks)

        self.combined_res = self._save_bbox_and_mask_res(nms_filtered_bboxes, nms_filtered_masks, store_mask=True)

        return self.combined_res

    def _single_thresh_filter(self, bbox_list: list, label_list: list, mask_list: list, score_thr=0.3):
        '''

        Args:
            bbox_list: [num_det,5=(x1,y1,x2,y2,score)]
            label_list: [num_det]
            mask_list: [num_dete,H,W]

        Returns:
            filtered with certain threshold score where are score > score threshold

            bboxes: [filtered_num_det,5=[x1,y1,x2,y2,score]]
            labels: [filtered_num_det]
            masks: [filtered_num_dete,H,W]
        '''

        needindexs = np.where((bbox_list[:, -1] > score_thr) & (label_list == SKETCH_CLASS_INDEX))
        bboxes = bbox_list[needindexs]
        labels = label_list[needindexs]
        masks = mask_list[needindexs]

        return bboxes, labels, masks

    def _nms(self, boxes: np.array, scores: np.array, iou_threshold: float):
        '''
        NMS algorithm to filter some rectangle lower than constraint threshold.
        Args:
            boxes: [num_det,4=[x1,y1,x2,y2] ]
            scores: [num_det]
            iou_threshold: thrsh_score

        Returns:
            All possible indicies after NMS filtered.

        Example:
            box =  np.array([[2,3.1,7,5],[3,4,8,4.8],[4,4,5.6,7],[0.1,0,8,1]])
            score = np.array([0.5, 0.3, 0.2, 0.4])

            indicies = numpy_nms(boxes=box, scores=score, iou_threshold=0.3)
        '''

        def box_area(boxes: np.array):
            return (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])

        def box_iou(box1: np.array, box2: np.array):
            area1 = box_area(box1)  # N
            area2 = box_area(box2)  # M
            # broadcasting, 两个数组各维度大小 从后往前对比一致， 或者 有一维度值为1；
            lt = np.maximum(box1[:, np.newaxis, :2], box2[:, :2])
            rb = np.minimum(box1[:, np.newaxis, 2:], box2[:, 2:])
            wh = rb - lt
            wh = np.maximum(0, wh)  # [N, M, 2]
            inter = wh[:, :, 0] * wh[:, :, 1]
            iou = inter / (area1[:, np.newaxis] + area2 - inter)
            return iou  # NxM

        idxs = scores.argsort()  # 按分数 降序排列的索引 [N]
        keep = []
        while idxs.size > 0:  # 统计数组中元素的个数
            max_score_index = idxs[-1]
            max_score_box = boxes[max_score_index][None, :]
            keep.append(max_score_index)
            if idxs.size == 1:
                break
            idxs = idxs[:-1]  # 将得分最大框 从索引中删除； 剩余索引对应的框 和 得分最大框 计算IoU；
            other_boxes = boxes[idxs]  # [?, 4]
            ious = box_iou(max_score_box, other_boxes)  # 一个框和其余框比较 1XM
            idxs = idxs[ious[0] <= iou_threshold]
        keep = np.array(keep)
        return keep

    def _save_bbox_and_mask_res(self, bbox_list: list, mask_list: list, store_mask: bool = False):
        '''
        Save detector results into a list.
        Args:
            bbox_list:  [num_det,4=[x,y,x,y]]
            mask_list: [num_det,H,W]
        Returns:
            res_list: [ dict{
                              bbox: [x1,y1,x2,y2],
                              mask: [H,W], numpy.array in binary and gray
                            }
                      ]
        '''
        if mask_list is None:
            store_mask = False
        res_list = []

        for index, (box, mask) in enumerate(zip(bbox_list, mask_list)):
            cur_res = {}
            x1, y1, x2, y2 = box.astype(np.int32)
            mask = mask * 255
            ret, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

            cur_res['bbox'] = [x1, y1, x2, y2]
            if store_mask:
                cur_res['mask'] = mask

            res_list.append(cur_res)

        return res_list

    def vis_result(self, img_data, bbox_list, mask_list):
        drawn_img_data = img_data
        for index, (box, mask) in enumerate(zip(bbox_list, mask_list)):
            x1, y1, x2, y2 = box.astype(np.int32)
            mask = mask * 255
            ret, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

            black = np.zeros_like(drawn_img_data)
            black = cv2.cvtColor(black, cv2.COLOR_BGR2GRAY)
            black = mask.astype(np.uint8)

            _, contours, hierarchy = cv2.findContours(black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) == 1:
                contours = np.array(contours).reshape((-1, 1, 2))
                cv2.polylines(drawn_img_data, [contours], isClosed=True, color=(0, 0, 255), thickness=3)
            else:
                for contour in contours:
                    contour = np.array(contour).reshape((-1, 1, 2))
                    cv2.polylines(drawn_img_data, [contour], isClosed=True, color=(0, 0, 255), thickness=3)

            alpha = 0.8

            mask = mask.astype(bool)
            random_colors = np.array([0, 255, 255])
            drawn_img_data[mask] = drawn_img_data[mask] * (1 - alpha) + random_colors * alpha

            cv2.rectangle(drawn_img_data, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.imshow('', drawn_img_data)
        cv2.waitKey(0)


######################################################################################################
# sketch estimator
from .top_down_eval import keypoints_from_heatmaps

SKETCH_INDEX_2_NAME = {
    0: 'nose',
    # neck = (left_shoulder+right_shoulder)/2
    # 1: 'neck',
    5: 'left_shoulder',
    6: 'right_shoulder',
    7: 'left_elbow',
    8: 'right_elbow',
    9: 'left_wrist',
    10: 'right_wrist',
    11: 'left_hip',
    12: 'right_hip',
    13: 'left_knee',
    14: 'right_knee',
    15: 'left_ankle',
    16: 'right_ankle',
    # hip_mid= (left_hip+right_hip)/2
    # -1: 'hip_mid',
}


class SketchPoseEstimator():
    def __init__(self,
                 model_path: str,
                 consider_keypoint_indicies: List[int] = [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]):
        assert osp.exists(model_path), 'Model path should exist!!'
        self.model_path = model_path
        self.session = ort.InferenceSession(model_path)
        self.output_tesnor_names = [node.name for node in self.session.get_outputs()]
        self.input_tensor_names = self.session.get_inputs()
        self.fine_width = 192
        self.fine_height = 256

        self.consider_keypoint_indicies = consider_keypoint_indicies

    def preprocess(self, img_data):
        '''

        Args:
            img_data: [H,W,C]

        Returns:
            img_tensor: [N=1,C,H,W] with Normalize and ToTensor()
        '''
        init_h, init_w, _ = img_data.shape
        img_tensor = cv2.dnn.blobFromImage(img_data, scalefactor=1.0 / 255,
                                           size=(self.fine_width, self.fine_height),
                                           mean=[0.485, 0.456, 0.406],
                                           swapRB=True,
                                           crop=False)
        return img_tensor

    def inference(self, img_path, bounding_bbox: List[int] = None, show_res=False):
        '''

        Args:
            img_path: str, path for image
            bounding_bbox: List[int], in [x1,y1,x2,y2] format. Default is None.
                           If exists, it will use for only given range for keypoints estimator.
            show_res: bool, if True, the result will be drawn with initial image data.

        Returns:
            keypoints_res: [V,C=2]
            joint_name_to_xy_dict: Dict { joint_name: (x,y) }
        '''
        assert osp.exists(img_path), 'Image path should exist!!'
        self.img_path = img_path
        img_data = cv2.imread(img_path)

        # check if bounding bbox exists
        if bounding_bbox is not None:
            l, t, r, b = [round(x) for x in bounding_bbox]
            img_data = img_data[t:b, l:r]

        self.img_data = img_data
        img_tensor = self.preprocess(img_data)
        heatmap = self.session.run(self.output_tesnor_names,
                                   input_feed={self.input_tensor_names[0].name: img_tensor})[0]

        keypoints_res, joint_name_to_xy_dict = self.postprocess(img_data, heatmap, show_res=show_res)

        return keypoints_res, joint_name_to_xy_dict

    def postprocess(self, img_data, heatmap, show_res=False):
        '''

        Args:
            img_data: [H,W,C]
            heatmap: [N,V,out_h,out_W]

        Returns:
            filtered_single_res: [V,C=2]
            joint_name_to_xy_dict: { joint_name: (x,y) }
        '''
        init_h, init_w, _ = img_data.shape
        detection_frame_x, detection_frame_y = 0, 0
        center_point_xy = np.array([[detection_frame_x + init_w * 0.5, detection_frame_y + init_h * 0.5]],
                                   dtype=np.float32)
        scale = np.array([[init_w / 200, init_h / 200]], dtype=np.float32)
        res = keypoints_from_heatmaps(heatmap, center_point_xy, scale)[0]
        # acquire all keypoints from first sketch
        self.all_single_res = copy.deepcopy(np.array(res.tolist()[0]))
        self.all_single_res = self.all_single_res.astype(np.int64)
        # [V,2]
        self.filtered_single_res = np.array(res.tolist()[0])[self.consider_keypoint_indicies]

        for i, point in enumerate(self.filtered_single_res):
            x, y = point
            self.filtered_single_res[i] = (x, y)

        # transfer float32 -> int32 for each keypoint's coordinate
        self.filtered_single_res = self.filtered_single_res.astype(np.int64)

        # store joint_name to xy in a dict {joint_name: (x,y)}
        self.joint_name_to_xy_dict = self._build_points_to_dict()

        if show_res:
            self.vis_pose_with_joint_dict()

        return self.filtered_single_res, self.joint_name_to_xy_dict

    def _build_points_to_dict(self):
        '''

        Returns: tresult dict { joint_name: (x,y) }

        '''
        tresult = OrderedDict()
        for index in self.consider_keypoint_indicies:
            node_name = SKETCH_INDEX_2_NAME[index]
            tresult[node_name] = self.all_single_res[index]

        # add neck and hip_mid by middle insert
        left_shoulder_x, left_shoulder_y = tresult['left_shoulder']
        right_shoulder_x, right_shoulder_y = tresult['right_shoulder']
        tresult['neck'] = [(left_shoulder_x + right_shoulder_x) // 2, (left_shoulder_y + right_shoulder_y) // 2]

        left_hip_x, left_hip_y = tresult['left_hip']
        right_hip_x, right_hip_y = tresult['right_hip']
        tresult['hip_mid'] = [(left_hip_x + right_hip_x) // 2, (left_hip_y + right_hip_y) // 2]

        return tresult

    def vis_pose_with_joint_dict(self):
        assert self.img_data is not None, 'Image data should not be None!!'
        assert self.joint_name_to_xy_dict is not None, 'Joint name to concrrect coordinate (x,y) should not be None!!'
        print(f'>> Total node cnt is {len(self.joint_name_to_xy_dict)}')

        drawn_img_data = self.img_data

        for node_name, point in self.joint_name_to_xy_dict.items():
            print(f'>> Current node name is {node_name}')
            x, y = point
            cv2.circle(drawn_img_data, (x, y), 4, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

        cv2.imshow('sketch_vis_result', drawn_img_data)
        cv2.waitKey(-1)
        return drawn_img_data


######################################################################################################

class SketchDetectorAndEstimator():
    def __init__(self, estimator_path: str, detector_path: str = None):
        '''

        Args:
            estimator_path: *.onnx file for estimator. It should be not None.
            detector_path: *.onnx file for detector. If it is None, the final process for inference will be not used.
        '''
        if detector_path is not None:
            assert osp.exists(detector_path), 'Path for detector should exist!!'
            self.detector = SketchDetector(model_path=detector_path)
        else:
            self.detector = None

        assert osp.exists(estimator_path), 'Path for estimator should exist!!'
        self.estimator = SketchPoseEstimator(model_path=estimator_path)

    def inference(self, img_path: str, show_res: bool = False,
                  need_mask: bool = False, morphops_iteration: int = 15,
                  out_dir: str = 'output'):
        '''

        Args:
            img_path: Source path for image.
            show_res: If show results ,final prediction will be visualized in a temporal window. Else, not shown.
            need_mask: If need mask, the output will use relative morphops operation to get mask.
            morphops_iteration: If need_mask=True, result will use morphops.
            out_dir: Base dir for saving dealt image data and config files.

        Returns:

        '''
        if self.detector is not None:
            detector_res: List[Dict[str, npt.NDArray[np.float32]]] = self.detector.inference(img_path=img_path,
                                                                                             show_res=show_res)
            # [x1,y1,x2,y2]
            bbox = detector_res[0]['bbox']

        # [V,C=2], Dict { joint_name: (x,y) }
        keypoints_res, joint_name_to_xy_dict = self.estimator.inference(img_path=img_path, bounding_bbox=bbox,
                                                                        show_res=show_res)
        # write result
        self._write_result(img_path, out_dir, bbox=bbox, joint_name_to_xy_dict=joint_name_to_xy_dict,
                           need_mask=need_mask, show_mask=show_res, morphops_iteration=morphops_iteration)

    def _write_result(self, img_path: str, out_dir: str, bbox: List[int] = None,
                      joint_name_to_xy_dict: Dict[str, npt.NDArray[np.int32]] = Dict,
                      need_mask: bool = True, morphops_iteration: int = 15, show_mask: bool = False):
        img_data = cv2.imread(img_path)
        if bbox is not None:
            img_h, img_w = bbox[-1] - bbox[1], bbox[-2] - bbox[0]
        else:
            img_h, img_w = img_data.shape[:2]

        img_h, img_w = int(img_h), int(img_w)

        skeleton = []
        # certainfy root joint
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['hip_mid']], 'name': 'root', 'parent': None})
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['hip_mid']], 'name': 'hip', 'parent': 'root'})
        # other joints
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['neck']], 'name': 'torso', 'parent': 'hip'})
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['nose']], 'name': 'nose', 'parent': 'torso'})
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['right_shoulder']], 'name': 'right_shoulder',
                         'parent': 'torso'})
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['right_elbow']], 'name': 'right_elbow',
                         'parent': 'right_shoulder'})
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['right_wrist']], 'name': 'right_hand',
                         'parent': 'right_elbow'})
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['left_shoulder']], 'name': 'left_shoulder',
                         'parent': 'torso'})
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['left_elbow']], 'name': 'left_elbow',
                         'parent': 'left_shoulder'})
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['left_wrist']], 'name': 'left_hand',
                         'parent': 'left_elbow'})
        skeleton.append(
            {'loc': [round(x) for x in joint_name_to_xy_dict['right_hip']], 'name': 'right_hip', 'parent': 'root'})
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['right_knee']], 'name': 'right_knee',
                         'parent': 'right_hip'})
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['right_ankle']], 'name': 'right_foot',
                         'parent': 'right_knee'})
        skeleton.append(
            {'loc': [round(x) for x in joint_name_to_xy_dict['left_hip']], 'name': 'left_hip', 'parent': 'root'})
        skeleton.append(
            {'loc': [round(x) for x in joint_name_to_xy_dict['left_knee']], 'name': 'left_knee', 'parent': 'left_hip'})
        skeleton.append({'loc': [round(x) for x in joint_name_to_xy_dict['left_ankle']], 'name': 'left_foot',
                         'parent': 'left_knee'})

        img_name, img_suffix = osp.basename(img_path).split('.')[0], osp.basename(img_path).split('.')[-1]
        output_base_dir = osp.join(out_dir, img_name)
        os.makedirs(output_base_dir, exist_ok=True)
        char_cfg_path = osp.join(output_base_dir, 'character_config.yaml')
        cropped_img_path = osp.join(output_base_dir, 'cropped_image.' + img_suffix)
        with open(char_cfg_path, 'w') as f:
            char_cfg = {'skeleton': skeleton, 'height': img_h, 'width': img_w}
            yaml.dump(char_cfg, f)

            if bbox is not None:
                l, t, r, b = [round(x) for x in bbox]
                img_data = img_data[t:b, l:r]

            cv2.imwrite(cropped_img_path, img_data)

        self.char_cfg_path, self.cropped_img_path = char_cfg_path, cropped_img_path
        print('>> Successfully save config file for character in', char_cfg_path, '!!')
        print('>> Successfully save cropped image file for character in', cropped_img_path, '!!')

        if need_mask:
            img_mask = self._get_mask(img_data=img_data, show_res=show_mask, morphops_iteration=morphops_iteration)

            mask_img_path = osp.join(output_base_dir, 'mask_image.' + img_suffix)

            cv2.imwrite(mask_img_path, img_mask)
            print('>> Successfully save segmented image file for character in', mask_img_path, '!!')
            self.mask_img_path = mask_img_path

    def _get_mask(self, img_data: npt.NDArray[np.uint8], show_res: bool = False, morphops_iteration=12):
        from skimage import measure
        from scipy import ndimage

        # find adaptive threshold
        img_data = np.min(img_data, axis=2)
        img_data = cv2.adaptiveThreshold(img_data, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 8)
        img_data = cv2.bitwise_not(img_data)

        # morphops operation
        # here, iteration for close and dialte is hyperparameter
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        img_data = cv2.morphologyEx(img_data, cv2.MORPH_CLOSE, kernel, iterations=morphops_iteration)
        img_data = cv2.morphologyEx(img_data, cv2.MORPH_DILATE, kernel, iterations=morphops_iteration)

        # floodfill (generate mask in the center and with padding for left, right, top and bottom)
        mask = np.zeros([img_data.shape[0] + 2, img_data.shape[1] + 2], np.uint8)
        mask[1:-1, 1:-1] = img_data.copy()

        # img_floodfill is the results of floodfill. Starts off all white
        img_data_floodfill = np.full(img_data.shape, 255, np.uint8)

        # choose 10 points along each image side. Use them as seed for floodfill
        h, w = img_data.shape[:2]
        for x in range(0, w - 1, 10):
            cv2.floodFill(img_data_floodfill, mask, (x, 0), 0)
            cv2.floodFill(img_data_floodfill, mask, (x, h - 1), 0)

        for y in range(0, h - 1, 10):
            cv2.floodFill(img_data_floodfill, mask, (0, y), 0)
            cv2.floodFill(img_data_floodfill, mask, (w - 1, y), 0)

        # remove the edge that exists character. It will influence for contour finding
        img_data_floodfill[0, :] = img_data_floodfill[-1, :] = img_data_floodfill[:, 0] = img_data_floodfill[:, -1] = 0

        # acquire largest contour
        mask2 = cv2.bitwise_not(img_data_floodfill)
        final_mask = None
        biggest_size = 0

        contours = measure.find_contours(mask2, 0.0)
        for c in contours:
            x = np.zeros(mask2.T.shape, np.uint8)
            cv2.fillPoly(x, [np.int32(c)], 1)
            size = len(np.where(x == 1)[0])
            if size > biggest_size:
                final_mask = x
                biggest_size = size

        if final_mask is None:
            msg = 'Found no contours within image'
            assert False, msg

        final_mask = ndimage.binary_fill_holes(final_mask).astype(int)
        final_mask = 255 * final_mask.astype(np.uint8)

        final_mask = final_mask.T

        if show_res:
            cv2.imshow('mask', final_mask)
            cv2.waitKey(-1)

        return final_mask


if __name__ == '__main__':
    args = get_args()
    sketch_executor = SketchDetectorAndEstimator(
        detector_path=args.detector_path,
        estimator_path=args.estimator_path
    )
    sketch_executor.inference(img_path=args.img_path, show_res=True, need_mask=True, morphops_iteration=args.mor_ite)
