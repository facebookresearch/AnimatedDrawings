# Copyright (c) Meta Platforms, Inc. and affiliates.

from setuptools import find_packages, setup

setup(
    name='animated_drawings',
    description="Companion code for `A Method For Automatically Animating Children's Drawings of the Human Form.`",
    author='FAIR',
    author_email='jesse.smith@meta.com',
    python_requires='>=3.8.13',
    install_requires=[
        'numpy== 1.23.3',
        'scipy==1.9.3',
        'scikit-image==0.19.3',
        'scikit-learn==1.1.2',
        'shapely==1.8.5.post1',
        'opencv-python==4.6.0.66',
        'Pillow==9.2.0',
        'glfw==2.5.5',
        'PyOpenGL==3.1.6',
        'PyYAML==6.0',
        'requests==2.28.1',
        'torchserve==0.7.0',
        'tqdm==4.64.1',
    ],
    packages=find_packages(),
)
