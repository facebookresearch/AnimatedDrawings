# -*- coding: utf-8 -*-
import json
import os
import zipfile
import time
from multiprocessing.dummy import Pool as ThreadPool
from collections import defaultdict

import torch
import numpy as np

''' Constant Configuration '''
delta1 = 1
mu = 1.7
delta2 = 2.65
gamma = 22.48
scoreThreds = 0.3
matchThreds = 5
alpha = 0.1
vis_thr = 0.2
oks_thr = 0.9
#pool = ThreadPool(4)


def oks_pose_nms(data, soft=False):
    kpts = defaultdict(list)
    post_data = []

    for item in data:
        img_id = item['image_id']
        kpts[img_id].append(item)

    for img_id, img_res in kpts.items():
        for n_p in img_res:
            box_score = n_p['score']
            kpt_score = 0
            valid_num = 0
            kpt = np.array(n_p['keypoints']).reshape(-1, 3)
            for n_jt in range(kpt.shape[0]):
                t_s = kpt[n_jt][2]
                if t_s > vis_thr:
                    kpt_score += t_s
                    valid_num += 1
            if valid_num != 0:
                kpt_score = kpt_score / valid_num
            n_p['score'] = kpt_score * box_score

        if soft:
            keep = soft_oks_nms(
                [img_res[i] for i in range(len(img_res))], oks_thr)
        else:
            keep = oks_nms(
                [img_res[i] for i in range(len(img_res))], oks_thr)

        if len(keep) == 0:
            post_data += img_res
        else:
            post_data += [img_res[_keep] for _keep in keep]

    return post_data


def oks_nms(kpts_db, thr, sigmas=None, vis_thr=None):
    """OKS NMS implementations.
    Args:
        kpts_db: keypoints.
        thr: Retain overlap < thr.
        sigmas: standard deviation of keypoint labelling.
        vis_thr: threshold of the keypoint visibility.
    Returns:
        np.ndarray: indexes to keep.
    """
    if len(kpts_db) == 0:
        return []

    scores = np.array([k['score'] for k in kpts_db])
    #kpts = np.array([k['keypoints'].flatten() for k in kpts_db])
    kpts = np.array([k['keypoints'] for k in kpts_db])
    areas = np.array([k['area'] for k in kpts_db])

    order = scores.argsort()[::-1]

    keep = []
    while len(order) > 0:
        i = order[0]
        keep.append(i)

        oks_ovr = oks_iou(kpts[i], kpts[order[1:]], areas[i], areas[order[1:]],
                          sigmas, vis_thr)

        inds = np.where(oks_ovr <= thr)[0]
        order = order[inds + 1]

    keep = np.array(keep)

    return keep


def soft_oks_nms(kpts_db, thr, max_dets=20, sigmas=None, vis_thr=None):
    """Soft OKS NMS implementations.
    Args:
        kpts_db
        thr: retain oks overlap < thr.
        max_dets: max number of detections to keep.
        sigmas: Keypoint labelling uncertainty.
    Returns:
        np.ndarray: indexes to keep.
    """
    if len(kpts_db) == 0:
        return []

    scores = np.array([k['score'] for k in kpts_db])
    kpts = np.array([k['keypoints'].flatten() for k in kpts_db])
    areas = np.array([k['area'] for k in kpts_db])

    order = scores.argsort()[::-1]
    scores = scores[order]

    keep = np.zeros(max_dets, dtype=np.intp)
    keep_cnt = 0
    while len(order) > 0 and keep_cnt < max_dets:
        i = order[0]

        oks_ovr = oks_iou(kpts[i], kpts[order[1:]], areas[i], areas[order[1:]],
                          sigmas, vis_thr)

        order = order[1:]
        scores = _rescore(oks_ovr, scores[1:], thr)

        tmp = scores.argsort()[::-1]
        order = order[tmp]
        scores = scores[tmp]

        keep[keep_cnt] = i
        keep_cnt += 1

    keep = keep[:keep_cnt]

    return keep


def oks_iou(g, d, a_g, a_d, sigmas=None, vis_thr=None):
    """Calculate oks ious.
    Args:
        g: Ground truth keypoints.
        d: Detected keypoints.
        a_g: Area of the ground truth object.
        a_d: Area of the detected object.
        sigmas: standard deviation of keypoint labelling.
        vis_thr: threshold of the keypoint visibility.
    Returns:
        list: The oks ious.
    """
    if sigmas is None:
        if len(g) == 408:   # 136keypoints
            sigmas = np.array([.26, .25, .25, .35, .35, .79, .79, .72, .72, .62,.62, 1.07, 1.07, .87, .87, .89, .89, .8,.8,.8,.89, .89, .89, .89, .89, .89,
                     .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25,
                     .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25,
                     .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25,
                     .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25,
                     .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25, .25])/10.0
        elif len(g) == 399:
            sigmas = np.array([.026, .025, .025, .035, .035, .079, .079, .072, .072, .062, .062, 0.107, 0.107, .087, .087, .089, .089,
                0.068, 0.066, 0.066, 0.092, 0.094, 0.094,
                0.042, 0.043, 0.044, 0.043, 0.040, 0.035, 0.031, 0.025, 0.020, 0.023, 0.029, 0.032, 0.037, 0.038, 0.043,
                0.041, 0.045, 0.013, 0.012, 0.011, 0.011, 0.012, 0.012, 0.011, 0.011, 0.013, 0.015, 0.009, 0.007, 0.007,
                0.007, 0.012, 0.009, 0.008, 0.016, 0.010, 0.017, 0.011, 0.009, 0.011, 0.009, 0.007, 0.013, 0.008, 0.011,
                0.012, 0.010, 0.034, 0.008, 0.008, 0.009, 0.008, 0.008, 0.007, 0.010, 0.008, 0.009, 0.009, 0.009, 0.007,
                0.007, 0.008, 0.011, 0.008, 0.008, 0.008, 0.01, 0.008,
                0.029, 0.022, 0.035, 0.037, 0.047, 0.026, 0.025, 0.024, 0.035, 0.018, 0.024, 0.022, 0.026, 0.017,
                0.021, 0.021, 0.032, 0.02, 0.019, 0.022, 0.031,
                0.029, 0.022, 0.035, 0.037, 0.047, 0.026, 0.025, 0.024, 0.035, 0.018, 0.024, 0.022, 0.026, 0.017,
                0.021, 0.021, 0.032, 0.02, 0.019, 0.022, 0.031])
        elif len(g) == 78:
            sigmas = np.array([.26, .25, .25, .35, .35, .79, .79, .72, .72, .62,.62, 1.07, 1.07, .87, .87, .89, .89, .8,.8,.8,.89, .89, .89, .89, .89, .89])/10.0
        else:
            sigmas = np.array([
                .26, .25, .25, .35, .35, .79, .79, .72, .72, .62, .62, 1.07, 1.07,
                .87, .87, .89, .89
            ]) / 10.0
    vars = (sigmas * 2)**2
    xg = g[0::3]
    yg = g[1::3]
    vg = g[2::3]
    ious = np.zeros(len(d))
    for n_d in range(0, len(d)):
        xd = d[n_d, 0::3]
        yd = d[n_d, 1::3]
        vd = d[n_d, 2::3]
        dx = xd - xg
        dy = yd - yg
        e = (dx**2 + dy**2) / vars / ((a_g + a_d[n_d]) / 2 + np.spacing(1)) / 2
        if vis_thr is not None:
            ind = list(vg > vis_thr) and list(vd > vis_thr)
            e = e[ind]
        ious[n_d] = np.sum(np.exp(-e)) / len(e) if len(e) != 0 else 0.0
    return ious


def _rescore(overlap, scores, thr, type='gaussian'):
    """Rescoring mechanism gaussian or linear.
    Args:
        overlap: calculated ious
        scores: target scores.
        thr: retain oks overlap < thr.
        type: 'gaussian' or 'linear'
    Returns:
        np.ndarray: indexes to keep
    """
    assert len(overlap) == len(scores)
    assert type in ['gaussian', 'linear']

    if type == 'linear':
        inds = np.where(overlap >= thr)[0]
        scores[inds] = scores[inds] * (1 - overlap[inds])
    else:
        scores = scores * np.exp(-overlap**2 / thr)

    return scores


def pose_nms(bboxes, bbox_scores, bbox_ids, pose_preds, pose_scores, areaThres=0):
    '''
    Parametric Pose NMS algorithm
    bboxes:         bbox locations list (n, 4)
    bbox_scores:    bbox scores list (n, 1)
    bbox_ids:       bbox tracking ids list (n, 1)
    pose_preds:     pose locations list (n, kp_num, 2)
    pose_scores:    pose scores list    (n, kp_num, 1)
    '''
    #global ori_pose_preds, ori_pose_scores, ref_dists

    pose_scores[pose_scores == 0] = 1e-5
    kp_nums = pose_preds.size()[1]
    res_bboxes, res_bbox_scores, res_bbox_ids, res_pose_preds, res_pose_scores, res_pick_ids = [],[],[],[],[],[]
    
    ori_bboxes = bboxes.clone()
    ori_bbox_scores = bbox_scores.clone()
    ori_bbox_ids = bbox_ids.clone()
    ori_pose_preds = pose_preds.clone()
    ori_pose_scores = pose_scores.clone()

    xmax = bboxes[:, 2]
    xmin = bboxes[:, 0]
    ymax = bboxes[:, 3]
    ymin = bboxes[:, 1]

    widths = xmax - xmin
    heights = ymax - ymin
    ref_dists = alpha * np.maximum(widths, heights)

    nsamples = bboxes.shape[0]
    human_scores = pose_scores.mean(dim=1)

    human_ids = np.arange(nsamples)
    mask = np.ones(len(human_ids)).astype(bool)
    
    # Do pPose-NMS
    pick = []
    merge_ids = []
    while(mask.any()):
        tensor_mask = torch.Tensor(mask)==True
        # Pick the one with highest score
        pick_id = torch.argmax(human_scores[tensor_mask])
        pick.append(human_ids[mask][pick_id])

        # Get numbers of match keypoints by calling PCK_match
        ref_dist = ref_dists[human_ids[mask][pick_id]]
        simi = get_parametric_distance(pick_id, pose_preds[tensor_mask], pose_scores[tensor_mask], ref_dist)
        num_match_keypoints = PCK_match(pose_preds[tensor_mask][pick_id], pose_preds[tensor_mask], ref_dist)

        # Delete humans who have more than matchThreds keypoints overlap and high similarity
        delete_ids = torch.from_numpy(np.arange(human_scores[tensor_mask].shape[0]))[((simi > gamma) | (num_match_keypoints >= matchThreds))]

        if delete_ids.shape[0] == 0:
            delete_ids = pick_id

        merge_ids.append(human_ids[mask][delete_ids])
        newmask = mask[mask]
        newmask[delete_ids] = False
        mask[mask] = newmask


    assert len(merge_ids) == len(pick)
    preds_pick = ori_pose_preds[pick]
    scores_pick = ori_pose_scores[pick]
    bbox_scores_pick = ori_bbox_scores[pick]
    bboxes_pick = ori_bboxes[pick]
    bbox_ids_pick = ori_bbox_ids[pick]
    #final_result = pool.map(filter_result, zip(scores_pick, merge_ids, preds_pick, pick, bbox_scores_pick))
    #final_result = [item for item in final_result if item is not None]

    for j in range(len(pick)):
        ids = np.arange(kp_nums)
        max_score = torch.max(scores_pick[j, ids, 0])

        if max_score < scoreThreds:
            continue

        # Merge poses
        merge_id = merge_ids[j]
        merge_pose, merge_score = p_merge_fast(
            preds_pick[j], ori_pose_preds[merge_id], ori_pose_scores[merge_id], ref_dists[pick[j]])

        max_score = torch.max(merge_score[ids])
        if max_score < scoreThreds:
            continue

        xmax = max(merge_pose[:, 0])
        xmin = min(merge_pose[:, 0])
        ymax = max(merge_pose[:, 1])
        ymin = min(merge_pose[:, 1])
        bbox = bboxes_pick[j].cpu().tolist()
        bbox_score = bbox_scores_pick[j].cpu()

        if (1.5 ** 2 * (xmax - xmin) * (ymax - ymin) < areaThres):
            continue


        res_bboxes.append(bbox)
        res_bbox_scores.append(bbox_score)
        res_bbox_ids.append(ori_bbox_ids[merge_id].tolist())
        res_pose_preds.append(merge_pose)
        res_pose_scores.append(merge_score)
        res_pick_ids.append(pick[j])

 

    return res_bboxes, res_bbox_scores, res_bbox_ids, res_pose_preds, res_pose_scores, res_pick_ids


def filter_result(args):
    score_pick, merge_id, pred_pick, pick, bbox_score_pick = args
    global ori_pose_preds, ori_pose_scores, ref_dists
    kp_nums = ori_pose_preds.size()[1]
    ids = np.arange(kp_nums)
    max_score = torch.max(score_pick[ids, 0])

    if max_score < scoreThreds:
        return None

    # Merge poses
    merge_pose, merge_score = p_merge_fast(
        pred_pick, ori_pose_preds[merge_id], ori_pose_scores[merge_id], ref_dists[pick])

    max_score = torch.max(merge_score[ids])
    if max_score < scoreThreds:
        return None

    xmax = max(merge_pose[:, 0])
    xmin = min(merge_pose[:, 0])
    ymax = max(merge_pose[:, 1])
    ymin = min(merge_pose[:, 1])

    if (1.5 ** 2 * (xmax - xmin) * (ymax - ymin) < 40 * 40.5):
        return None

    return {
        'keypoints': merge_pose - 0.3,
        'kp_score': merge_score,
        'proposal_score': torch.mean(merge_score) + bbox_score_pick + 1.25 * max(merge_score)
    }


def p_merge(ref_pose, cluster_preds, cluster_scores, ref_dist):
    '''
    Score-weighted pose merging
    INPUT:
        ref_pose:       reference pose          -- [kp_num, 2]
        cluster_preds:  redundant poses         -- [n, kp_num, 2]
        cluster_scores: redundant poses score   -- [n, kp_num, 1]
        ref_dist:       reference scale         -- Constant
    OUTPUT:
        final_pose:     merged pose             -- [kp_num, 2]
        final_score:    merged score            -- [kp_num]
    '''
    dist = torch.sqrt(torch.sum(
        torch.pow(ref_pose[np.newaxis, :] - cluster_preds, 2),
        dim=2
    ))  # [n, kp_num]

    kp_num = ref_pose.size()[0]
    ref_dist = min(ref_dist, 15)

    mask = (dist <= ref_dist)
    final_pose = torch.zeros(kp_num, 2)
    final_score = torch.zeros(kp_num)

    if cluster_preds.dim() == 2:
        cluster_preds.unsqueeze_(0)
        cluster_scores.unsqueeze_(0)
    if mask.dim() == 1:
        mask.unsqueeze_(0)

    for i in range(kp_num):
        cluster_joint_scores = cluster_scores[:, i][mask[:, i]]  # [k, 1]
        cluster_joint_location = cluster_preds[:, i, :][mask[:, i].unsqueeze(
            -1).repeat(1, 2)].view((torch.sum(mask[:, i]), -1))

        # Get an normalized score
        normed_scores = cluster_joint_scores / torch.sum(cluster_joint_scores)

        # Merge poses by a weighted sum
        final_pose[i, 0] = torch.dot(cluster_joint_location[:, 0], normed_scores.squeeze(-1))
        final_pose[i, 1] = torch.dot(cluster_joint_location[:, 1], normed_scores.squeeze(-1))

        final_score[i] = torch.dot(cluster_joint_scores.transpose(0, 1).squeeze(0), normed_scores.squeeze(-1))

    return final_pose, final_score


def p_merge_fast(ref_pose, cluster_preds, cluster_scores, ref_dist):
    '''
    Score-weighted pose merging
    INPUT:
        ref_pose:       reference pose          -- [kp_num, 2]
        cluster_preds:  redundant poses         -- [n, kp_num, 2]
        cluster_scores: redundant poses score   -- [n, kp_num, 1]
        ref_dist:       reference scale         -- Constant
    OUTPUT:
        final_pose:     merged pose             -- [kp_num, 2]
        final_score:    merged score            -- [kp_num]
    '''
    dist = torch.sqrt(torch.sum(
        torch.pow(ref_pose[np.newaxis, :] - cluster_preds, 2),
        dim=2
    ))

    kp_num = ref_pose.size()[0]
    ref_dist = min(ref_dist, 15)

    # patch
    try: 
        ref_dist = ref_dist.float() 
    except:  
        pass  

    mask = (dist <= ref_dist)
    final_pose = torch.zeros(kp_num, 2)
    final_score = torch.zeros(kp_num)

    if cluster_preds.dim() == 2:
        cluster_preds.unsqueeze_(0)
        cluster_scores.unsqueeze_(0)
    if mask.dim() == 1:
        mask.unsqueeze_(0)

    # Weighted Merge
    masked_scores = cluster_scores.mul(mask.float().unsqueeze(-1))
    normed_scores = masked_scores / torch.sum(masked_scores, dim=0)

    final_pose = torch.mul(cluster_preds, normed_scores.repeat(1, 1, 2)).sum(dim=0)
    final_score = torch.mul(masked_scores, normed_scores).sum(dim=0)
    return final_pose, final_score


def get_parametric_distance(i, all_preds, keypoint_scores, ref_dist):
    pick_preds = all_preds[i]
    pred_scores = keypoint_scores[i]
    dist = torch.sqrt(torch.sum(
        torch.pow(pick_preds[np.newaxis, :] - all_preds, 2),
        dim=2
    ))
    mask = (dist <= 1)

    kp_nums = all_preds.size()[1]
    # Define a keypoints distance
    score_dists = torch.zeros(all_preds.shape[0], kp_nums)
    keypoint_scores.squeeze_()
    if keypoint_scores.dim() == 1:
        keypoint_scores.unsqueeze_(0)
    if pred_scores.dim() == 1:
        pred_scores.unsqueeze_(1)
    # The predicted scores are repeated up to do broadcast
    pred_scores = pred_scores.repeat(1, all_preds.shape[0]).transpose(0, 1)

    score_dists[mask] = torch.tanh(pred_scores[mask] / delta1) * torch.tanh(keypoint_scores[mask] / delta1)

    point_dist = torch.exp((-1) * dist / delta2)
    final_dist = torch.sum(score_dists, dim=1) + mu * torch.sum(point_dist, dim=1)

    return final_dist


def PCK_match(pick_pred, all_preds, ref_dist):
    dist = torch.sqrt(torch.sum(
        torch.pow(pick_pred[np.newaxis, :] - all_preds, 2),
        dim=2
    ))
    ref_dist = min(ref_dist, 7)
    num_match_keypoints = torch.sum(
        dist / ref_dist <= 1,
        dim=1
    )

    return num_match_keypoints


def write_json(all_results, outputpath, form=None, for_eval=False):
    '''
    all_result: result dict of predictions
    outputpath: output directory
    '''
    json_results = []
    json_results_cmu = {}
    for im_res in all_results:
        im_name = im_res['imgname']
        for human in im_res['result']:
            keypoints = []
            result = {}
            if for_eval:
                result['image_id'] = int(os.path.basename(im_name).split('.')[0].split('_')[-1])
            else:
                result['image_id'] = os.path.basename(im_name)
            result['category_id'] = 1

            kp_preds = human['keypoints']
            kp_scores = human['kp_score']
            pro_scores = human['proposal_score']
            for n in range(kp_scores.shape[0]):
                keypoints.append(float(kp_preds[n, 0]))
                keypoints.append(float(kp_preds[n, 1]))
                keypoints.append(float(kp_scores[n]))
            result['keypoints'] = keypoints
            result['score'] = float(pro_scores)
            if 'box' in human.keys():
                result['box'] = human['box']
            #pose track results by PoseFlow
            if 'idx' in human.keys():
                result['idx'] = human['idx']

            if form == 'cmu': # the form of CMU-Pose
                if result['image_id'] not in json_results_cmu.keys():
                    json_results_cmu[result['image_id']]={}
                    json_results_cmu[result['image_id']]['version']="AlphaPose v0.3"
                    json_results_cmu[result['image_id']]['bodies']=[]
                tmp={'joints':[]}
                result['keypoints'].append((result['keypoints'][15]+result['keypoints'][18])/2)
                result['keypoints'].append((result['keypoints'][16]+result['keypoints'][19])/2)
                result['keypoints'].append((result['keypoints'][17]+result['keypoints'][20])/2)
                indexarr=[0,51,18,24,30,15,21,27,36,42,48,33,39,45,6,3,12,9]
                for i in indexarr:
                    tmp['joints'].append(result['keypoints'][i])
                    tmp['joints'].append(result['keypoints'][i+1])
                    tmp['joints'].append(result['keypoints'][i+2])
                json_results_cmu[result['image_id']]['bodies'].append(tmp)
            elif form == 'open': # the form of OpenPose
                if result['image_id'] not in json_results_cmu.keys():
                    json_results_cmu[result['image_id']]={}
                    json_results_cmu[result['image_id']]['version']="AlphaPose v0.3"
                    json_results_cmu[result['image_id']]['people']=[]
                tmp={'pose_keypoints_2d':[]}
                result['keypoints'].append((result['keypoints'][15]+result['keypoints'][18])/2)
                result['keypoints'].append((result['keypoints'][16]+result['keypoints'][19])/2)
                result['keypoints'].append((result['keypoints'][17]+result['keypoints'][20])/2)
                indexarr=[0,51,18,24,30,15,21,27,36,42,48,33,39,45,6,3,12,9]
                for i in indexarr:
                    tmp['pose_keypoints_2d'].append(result['keypoints'][i])
                    tmp['pose_keypoints_2d'].append(result['keypoints'][i+1])
                    tmp['pose_keypoints_2d'].append(result['keypoints'][i+2])
                json_results_cmu[result['image_id']]['people'].append(tmp)
            else:
                json_results.append(result)

    if form == 'cmu': # the form of CMU-Pose
        with open(os.path.join(outputpath,'alphapose-results.json'), 'w') as json_file:
            json_file.write(json.dumps(json_results_cmu))
            if not os.path.exists(os.path.join(outputpath,'sep-json')):
                os.mkdir(os.path.join(outputpath,'sep-json'))
            for name in json_results_cmu.keys():
                with open(os.path.join(outputpath,'sep-json',name.split('.')[0]+'.json'),'w') as json_file:
                    json_file.write(json.dumps(json_results_cmu[name]))
    elif form == 'open': # the form of OpenPose
        with open(os.path.join(outputpath,'alphapose-results.json'), 'w') as json_file:
            json_file.write(json.dumps(json_results_cmu))
            if not os.path.exists(os.path.join(outputpath,'sep-json')):
                os.mkdir(os.path.join(outputpath,'sep-json'))
            for name in json_results_cmu.keys():
                with open(os.path.join(outputpath,'sep-json',name.split('.')[0]+'.json'),'w') as json_file:
                    json_file.write(json.dumps(json_results_cmu[name]))
    else:
        with open(os.path.join(outputpath,'alphapose-results.json'), 'w') as json_file:
            json_file.write(json.dumps(json_results))

