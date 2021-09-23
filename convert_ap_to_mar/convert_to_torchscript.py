import argparse
import torch
import cv2
import numpy as np

from alphapose.models import builder
from alphapose.utils.config import update_config

print(torch.__version__)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transform alphapose to torchscript.')
    parser.add_argument('--cfg', type=str, help='alphapose cfg file')
    parser.add_argument('--pth', type=str, help='alphapose weights file')
    args = parser.parse_args()

    cfg = update_config(args.cfg)

    # Load pose model
    pose_model = builder.build_sppe(cfg.MODEL, preset_cfg=cfg.DATA_PRESET)
    pose_model.load_state_dict(torch.load(args.pth, map_location=device))
    pose_model.to(device)
    pose_model.eval()

    # Create sample
    image = np.random.randint(0, 255, (3, 256, 192), dtype=np.uint8)
    img = torch.from_numpy(image).float()
    img /= 255
    img[0].add_(-0.406)
    img[1].add_(-0.457)
    img[2].add_(-0.480)
    imgs = img.unsqueeze(0)
    imgs = imgs.to(device)

    # Convert to torchscript
    traced_model = torch.jit.trace(pose_model, imgs)

    # Save torchscript model
    traced_model.save(args.pth.replace(".pth", ".jit"))

