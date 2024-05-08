# easy_ViTPose
<p align="center">
<img src="https://user-images.githubusercontent.com/24314647/236082274-b25a70c8-9267-4375-97b0-eddf60a7dfc6.png" width=375> easy_ViTPose
</p>

## Accurate 2d human and animal pose estimation

<a target="_blank" href="https://colab.research.google.com/github/JunkyByte/easy_ViTPose/blob/main/colab_demo.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

### Easy to use SOTA `ViTPose` [Y. Xu et al., 2022] models for fast inference.  
We provide all the VitPose original models, converted for inference, with single dataset format output.

## Results
![resimg](https://github.com/JunkyByte/easy_ViTPose/assets/24314647/51c0777f-b268-448a-af02-9a3537f288d8)

https://github.com/JunkyByte/easy_ViTPose/assets/24314647/e9a82c17-6e99-4111-8cc8-5257910cb87e

https://github.com/JunkyByte/easy_ViTPose/assets/24314647/63af44b1-7245-4703-8906-3f034a43f9e3

(Credits dance: https://www.youtube.com/watch?v=p-rSdt0aFuw )  
(Credits zebras: https://www.youtube.com/watch?v=y-vELRYS8Yk )

## Features
- Image / Video / Webcam support
- Video support using SORT algorithm to track bboxes between frames
- Torch / ONNX / Tensorrt inference
- Runs the original VitPose checkpoints from [ViTAE-Transformer/ViTPose](https://github.com/ViTAE-Transformer/ViTPose)
- 4 ViTPose architectures with different sizes and performances (s: small, b: base, l: large, h: huge)
- Multi skeleton and dataset: (AIC / MPII / COCO / COCO + FEET / COCO WHOLEBODY / APT36k / AP10k)
- Human / Animal pose estimation
- cpu / gpu / metal support
- show and save images / videos and output to json

We run YOLOv8 for detection, it does not provide complete animal detection. You can finetune a custom yolo model to detect the animal you are interested in,
if you do please open an issue, we might want to integrate other models for detection.

### Benchmark:
Realtime >30 fps with modern nvidia gpus and apple silicon (using metal!).  
Here some performance results (end to end inference pipeline)  
```
GTX1080ti + yolo small tensorrt + vit-b tensorrt model: 100fps
GTX1080ti + yolo small tensorrt + vit-s tensorrt model: 175fps
AIR M2 2023 + yolo nano torch + vit-s torch model (metal): >30fps (with a mean of 4 poses per frame)
```

### Skeleton reference
There are multiple skeletons for different dataset. Check the definition here [visualization.py](https://github.com/JunkyByte/easy_ViTPose/blob/main/easy_ViTPose/vit_utils/visualization.py).

## Installation and Usage
> [!IMPORTANT]
> Install `torch>2.0 with cuda / mps support` by yourself.
> also check `requirements_gpu.txt`.

```bash
git clone git@github.com:JunkyByte/easy_ViTPose.git
cd easy_ViTPose/
pip install -e .
pip install -r requirements.txt
```

### Download models
- Download the models from [Huggingface](https://huggingface.co/JunkyByte/easy_ViTPose)
We provide torch models for every dataset and architecture.  
If you want to run onnx / tensorrt inference download the appropriate torch ckpt and use `export.py` to convert it.  
You can use `ultralytics` `yolo export` command to export yolo to onnx and tensorrt as well.

#### Export to onnx and tensorrt
```bash
$ python export.py --help
usage: export.py [-h] --model-ckpt MODEL_CKPT --model-name {s,b,l,h} [--output OUTPUT] [--dataset DATASET]

optional arguments:
  -h, --help            show this help message and exit
  --model-ckpt MODEL_CKPT
                        The torch model that shall be used for conversion
  --model-name {s,b,l,h}
                        [s: ViT-S, b: ViT-B, l: ViT-L, h: ViT-H]
  --output OUTPUT       File (without extension) or dir path for checkpoint output
  --dataset DATASET     Name of the dataset. If None it"s extracted from the file name. ["coco", "coco_25",
                        "wholebody", "mpii", "ap10k", "apt36k", "aic"]
```

### Run inference
To run inference from command line you can use the `inference.py` script as follows:  
```bash
$ python inference.py --help
usage: inference.py [-h] [--input INPUT] [--output-path OUTPUT_PATH] --model MODEL [--yolo YOLO] [--dataset DATASET]
                    [--det-class DET_CLASS] [--model-name {s,b,l,h}] [--yolo-size YOLO_SIZE]
                    [--conf-threshold CONF_THRESHOLD] [--rotate {0,90,180,270}] [--yolo-step YOLO_STEP]
                    [--single-pose] [--show] [--show-yolo] [--show-raw-yolo] [--save-img] [--save-json]

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT         path to image / video or webcam ID (=cv2)
  --output-path OUTPUT_PATH
                        output path, if the path provided is a directory output files are "input_name
                        +_result{extension}".
  --model MODEL         checkpoint path of the model
  --yolo YOLO           checkpoint path of the yolo model
  --dataset DATASET     Name of the dataset. If None it"s extracted from the file name. ["coco", "coco_25",
                        "wholebody", "mpii", "ap10k", "apt36k", "aic"]
  --det-class DET_CLASS
                        ["human", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
                        "animals"]
  --model-name {s,b,l,h}
                        [s: ViT-S, b: ViT-B, l: ViT-L, h: ViT-H]
  --yolo-size YOLO_SIZE
                        YOLOv8 image size during inference
  --conf-threshold CONF_THRESHOLD
                        Minimum confidence for keypoints to be drawn. [0, 1] range
  --rotate {0,90,180,270}
                        Rotate the image of [90, 180, 270] degress counterclockwise
  --yolo-step YOLO_STEP
                        The tracker can be used to predict the bboxes instead of yolo for performance, this flag
                        specifies how often yolo is applied (e.g. 1 applies yolo every frame). This does not have any
                        effect when is_video is False
  --single-pose         Do not use SORT tracker because single pose is expected in the video
  --show                preview result during inference
  --show-yolo           draw yolo results
  --show-raw-yolo       draw yolo result before that SORT is applied for tracking (only valid during video inference)
  --save-img            save image results
  --save-json           save json results
```

You can run inference from code as follows:
```python
import cv2
from easy_ViTPose import VitInference

# Image to run inference RGB format
img = cv2.imread('./examples/img1.jpg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# set is_video=True to enable tracking in video inference
# be sure to use VitInference.reset() function to reset the tracker after each video
# There are a few flags that allows to customize VitInference, be sure to check the class definition
model_path = './ckpts/vitpose-s-coco_25.pth'
yolo_path = './yolov5s.pth'

# If you want to use MPS (on new macbooks) use the torch checkpoints for both ViTPose and Yolo
# If device is None will try to use cuda -> mps -> cpu (otherwise specify 'cpu', 'mps' or 'cuda')
# dataset and det_class parameters can be inferred from the ckpt name, but you can specify them.
model = VitInference(model_path, yolo_path, model_name='s', yolo_size=320, is_video=False, device=None)

# Infer keypoints, output is a dict where keys are person ids and values are keypoints (np.ndarray (25, 3): (y, x, score))
# If is_video=True the IDs will be consistent among the ordered video frames.
keypoints = model.inference(img)

# call model.reset() after each video

img = model.draw(show_yolo=True)  # Returns RGB image with drawings
cv2.imshow('image', cv2.cvtColor(img, cv2.COLOR_RGB2BGR)); cv2.waitKey(0)
```
> [!NOTE]
> If the input file is a video [SORT](https://github.com/abewley/sort) is used to track people IDs and output consistent identifications.

### OUTPUT json format
The output format of the json files:

```
{
    "keypoints":
    [  # The list of frames, len(json['keypoints']) == len(video)
        {  # For each frame a dict
            "0": [  #  keys are id to track people and value the keypoints
                [121.19, 458.15, 0.99], # Each keypoint is (y, x, score)
                [110.02, 469.43, 0.98],
                [110.86, 445.04, 0.99],
            ],
            "1": [
                ...
            ],
        },
        {
            "0": [
                [122.19, 458.15, 0.91],
                [105.02, 469.43, 0.95],
                [122.86, 445.04, 0.99],
            ],
            "1": [
                ...
            ]
        }
    ],
    "skeleton":
    {  # Skeleton reference, key the idx, value the name
        "0": "nose",
        "1": "left_eye",
        "2": "right_eye",
        "3": "left_ear",
        "4": "right_ear",
        "5": "neck",
        ...
    }
}
```

## Finetuning
Finetuning is possible but not officially supported right now. If you would like to finetune and need help open an issue.  
You can check `train.py`, `datasets/COCO.py` and `config.yaml` for details.

---

## TODO:
- refactor finetuning
- benchmark and check bottlenecks of inference pipeline
- parallel batched inference
- other minor fixes
- yolo version for animal pose, check https://github.com/JunkyByte/easy_ViTPose/pull/18
- solve cuda exceptions on script exit when using tensorrt (no idea how)
- add infos about inferred informations during inference, better output of inference status (device etc)
- check if is possible to make colab work without runtime restart

Feel free to open issues, pull requests and contribute on these TODOs.

## Reference
Thanks to the VitPose authors and their official implementation [ViTAE-Transformer/ViTPose](https://github.com/ViTAE-Transformer/ViTPose).  
The SORT code is taken from [abewley/sort](https://github.com/abewley/sort)
