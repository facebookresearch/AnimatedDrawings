# Ultralytics YOLO 🚀, AGPL-3.0 license
import os.path as osp
import sys

sys.path.append(osp.join(osp.dirname(__file__), '..'))

__version__ = '8.0.145'

from .hub import start
from .models import RTDETR, SAM, YOLO
from .models.fastsam import FastSAM
from .models.nas import NAS
from .utils import SETTINGS as settings
from .utils.checks import check_yolo as checks
from .utils.downloads import download

__all__ = '__version__', 'YOLO', 'NAS', 'SAM', 'FastSAM', 'RTDETR', 'checks', 'download', 'start', 'settings'  # allow simpler import
