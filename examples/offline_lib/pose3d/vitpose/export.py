import os
import torch
import argparse

from easy_ViTPose.vit_models.model import ViTPose
from easy_ViTPose.vit_utils.util import infer_dataset_by_path, dyn_model_import


parser = argparse.ArgumentParser()
parser.add_argument('--model-ckpt', type=str, required=True,
                    help='The torch model that shall be used for conversion')
parser.add_argument('--model-name', type=str, required=True, choices=['s', 'b', 'l', 'h'],
                    help='[s: ViT-S, b: ViT-B, l: ViT-L, h: ViT-H]')
parser.add_argument('--output', type=str, default='ckpts/',
                    help='File (without extension) or dir path for checkpoint output')
parser.add_argument('--dataset', type=str, required=False, default=None,
                    help='Name of the dataset. If None it"s extracted from the file name. \
                          ["coco", "coco_25", "wholebody", "mpii", "ap10k", "apt36k", "aic"]')
args = parser.parse_args()


# Get dataset and model_cfg
dataset = args.dataset
if dataset is None:
    dataset = infer_dataset_by_path(args.model_ckpt)
assert dataset in ['mpii', 'coco', 'coco_25', 'wholebody', 'aic', 'ap10k', 'apt36k'], \
    'The specified dataset is not valid'
model_cfg = dyn_model_import(dataset, args.model_name)

# Convert to onnx and save
print('>>> Converting to ONNX')
CKPT_PATH = args.model_ckpt
C, H, W = (3, 256, 192)

model = ViTPose(model_cfg)

ckpt = torch.load(CKPT_PATH, map_location='cpu')
if 'state_dict' in ckpt:
    ckpt = ckpt['state_dict']

model.load_state_dict(ckpt)
model.eval()

input_names = ["input_0"]
output_names = ["output_0"]

device = next(model.parameters()).device
inputs = torch.randn(1, C, H, W).to(device)

dynamic_axes = {'input_0': {0: 'batch_size'},
                'output_0': {0: 'batch_size'}}

out_name = os.path.basename(args.model_ckpt).replace('.pth', '')
if not os.path.isdir(args.output): out_name = os.path.basename(args.output)
output_onnx = os.path.join(os.path.dirname(args.output), out_name + '.onnx')

torch_out = torch.onnx.export(model, inputs, output_onnx, export_params=True, verbose=False,
                              input_names=input_names, output_names=output_names,
                              opset_version=11, dynamic_axes=dynamic_axes)
print(f">>> Saved at: {os.path.abspath(output_onnx)}")
print('=' * 80)
print()

try:
    import tensorrt as trt
except ModuleNotFoundError:
    print('>>> TRT module not found, skipping')
    import sys
    sys.exit()

# From yolo convert script, onnx -> trt
print('>>> Converting to TRT')
def export_engine(onnx, im, file, half, dynamic, workspace=4, verbose=False, prefix='Tensorrt'):
    logger = trt.Logger(trt.Logger.INFO)
    if verbose:
        logger.min_severity = trt.Logger.Severity.VERBOSE

    builder = trt.Builder(logger)
    config = builder.create_builder_config()
    config.max_workspace_size = workspace * 1 << 30

    flag = (1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    network = builder.create_network(flag)
    parser = trt.OnnxParser(network, logger)
    if not parser.parse_from_file(str(onnx)):
        raise RuntimeError(f'failed to load ONNX file: {onnx}')

    inputs = [network.get_input(i) for i in range(network.num_inputs)]
    outputs = [network.get_output(i) for i in range(network.num_outputs)]
    for inp in inputs:
        print(f'{prefix} input "{inp.name}" with shape{inp.shape} {inp.dtype}')
    for out in outputs:
        print(f'{prefix} output "{out.name}" with shape{out.shape} {out.dtype}')

    if dynamic:
        if im.shape[0] <= 1:
            print(f'{prefix} WARNING ⚠️ --dynamic model requires maximum --batch-size argument')
        profile = builder.create_optimization_profile()
        for inp in inputs:
            profile.set_shape(inp.name, (1, *im.shape[1:]), (max(1, im.shape[0] // 2), *im.shape[1:]), im.shape)
        config.add_optimization_profile(profile)

    print(f'{prefix} building FP{16 if builder.platform_has_fast_fp16 and half else 32} engine')
    if builder.platform_has_fast_fp16 and half:
        config.set_flag(trt.BuilderFlag.FP16)
    with builder.build_engine(network, config) as engine, open(file, 'wb') as t:
        t.write(engine.serialize())
    return True


# Export
output_trt = output_onnx.replace('.onnx', '.engine')

input_names = ["input_0"]
output_names = ["output_0"]

device = next(model.parameters()).device
inputs = torch.randn(1, C, H, W).to(device)

export_engine(output_onnx, inputs, output_trt, False, True, verbose=False)
print(f">>> Saved at: {os.path.abspath(output_trt)}")
