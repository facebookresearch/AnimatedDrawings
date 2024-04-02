import torch
import os
import argparse
import copy

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, required=True)
    parser.add_argument('--prefix', type=str, required=True)
    parser.add_argument('--target', type=str, default=None)
    args = parser.parse_args()
    return args

def main():

    args = parse_args()

    if args.target is None:
        args.target = '/'.join(args.source.split('/')[:-1])

    ckpt = torch.load(args.source, map_location='cpu')
    
    experts = dict()

    new_ckpt = copy.deepcopy(ckpt)

    state_dict = new_ckpt['state_dict']

    for key, value in state_dict.items():
        if 'mlp.experts' in key:
            experts[key] = value

    keys = ckpt['state_dict'].keys()

    weight_names = ['keypoint_head.deconv_layers.0.weight', 
                    'keypoint_head.deconv_layers.1.weight', 
                    'keypoint_head.deconv_layers.1.bias', 
                    'keypoint_head.deconv_layers.1.running_mean', 
                    'keypoint_head.deconv_layers.1.running_var', 
                    'keypoint_head.deconv_layers.1.num_batches_tracked', 
                    'keypoint_head.deconv_layers.3.weight', 
                    'keypoint_head.deconv_layers.4.weight', 
                    'keypoint_head.deconv_layers.4.bias', 
                    'keypoint_head.deconv_layers.4.running_mean', 
                    'keypoint_head.deconv_layers.4.running_var', 
                    'keypoint_head.deconv_layers.4.num_batches_tracked', 
                    'keypoint_head.final_layer.weight', 
                    'keypoint_head.final_layer.bias']
    
    target_expert = 0
    new_ckpt = copy.deepcopy(ckpt)

    for key in keys:
        if 'mlp.fc2' in key:
            value = new_ckpt['state_dict'][key]
            value = torch.cat([value, experts[key.replace('fc2.', f'experts.{target_expert}.')]], dim=0)
            new_ckpt['state_dict'][key] = value

    # remove unnecessary part in the state dict
    for j in range(5):
        # remove associate part
        for tensor_name in weight_names:
            new_ckpt['state_dict'].pop(tensor_name.replace('keypoint_head',
                                                           f'associate_keypoint_heads.{j}'))
    # remove expert part
    keys = new_ckpt['state_dict'].keys()
    for key in list(keys):
        if 'expert' in key:
            new_ckpt['state_dict'].pop(key)

    torch.save(new_ckpt, os.path.join(args.target, args.prefix + 'coco.pth'))

    names = ['aic', 'mpii', 'ap10k', 'apt36k','wholebody']
    num_keypoints = [14, 16, 17, 17, 133]
    exist_range = True

    for i in range(5):

        new_ckpt = copy.deepcopy(ckpt)

        target_expert = i + 1

        for key in keys:
            if 'mlp.fc2' in key:
                expert_key = key.replace('fc2.', f'experts.{target_expert}.')
                if expert_key in experts:
                    value = new_ckpt['state_dict'][key]
                    value = torch.cat([value, experts[expert_key]], dim=0)
                else:
                    exist_range = False

                new_ckpt['state_dict'][key] = value

        if not exist_range:
            break

        for tensor_name in weight_names:
            new_ckpt['state_dict'][tensor_name] = new_ckpt['state_dict'][tensor_name.replace('keypoint_head',
                                                                                             f'associate_keypoint_heads.{i}')]

        for tensor_name in ['keypoint_head.final_layer.weight', 'keypoint_head.final_layer.bias']:
            new_ckpt['state_dict'][tensor_name] = new_ckpt['state_dict'][tensor_name][:num_keypoints[i]]
        
        # remove unnecessary part in the state dict
        for j in range(5):
            # remove associate part
            for tensor_name in weight_names:
                new_ckpt['state_dict'].pop(tensor_name.replace('keypoint_head',
                                                               f'associate_keypoint_heads.{j}'))
        # remove expert part
        keys = new_ckpt['state_dict'].keys()
        for key in list(keys):
            if 'expert' in key:
                new_ckpt['state_dict'].pop(key)
            
        torch.save(new_ckpt, os.path.join(args.target, f'{args.prefix}{names[i]}.pth'))

if __name__ == '__main__':
    main()
