# sketch_rig

This is the first of the two repos that comprise the Animating Children's Sketches project. This repo contains the code necessary to detect humanoid characters within a drawing, segment them from the background, predict joint locations onto the character, and combine the results into a rigged character that can be animated by sketch_animate.

# Setup 
  

### Get Detectron2 and Alphapose weights
Download the finetuned Detectron2 weights from Drive: https://drive.google.com/file/d/1tyhVUXbWf5CeYAoHHbrOVtm72CBUNF37/view?usp=sharing

Download the finetuned Alphapose weights from Drive: https://drive.google.com/file/d/1v3gEjvU4zWhNbvobNfsmIIkpbgjvvs_-/view?usp=sharing

Add the following to ~/.bashrc
  
    DETECTRON2_WEIGHTS_LOC=<absolute path of detectron2 weights>
    ALPHAPOSE_WEIGHTS_LOC=<absolute path of alphapose weights>
    D2_VIRTUAL_ENV_NAME=<a name for your detectron2 conda virtualenv> # 'detectron2', for example
    AP_VIRTUAL_ENV_NAME=<a name for your alphapose conda virtualenv> # 'alphapose', for example

Reload ~/.bashrc
    
    source ~/.bashrc

### Install Detectron2 on your machine. 

This is what I used to install it on the FAIR cluster

    module load cuda/10.2
    conda create  --name ${D2_VIRTUAL_ENV_NAME} python=3.7.9
    conda activate ${D2_VIRTUAL_ENV_NAME}
    conda install opencv
    conda install pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch
    python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
    conda install scikit-image
    conda install scikit-learn
    conda deactivate

### Install Alphapose on your machine. 

This is how I installed it on the FAIR cluster

    conda create  --name ${AP_VIRTUAL_ENV_NAME} python=3.6 -y
    conda activate ${AP_VIRTUAL_ENV_NAME}
    # The following is from here: https://github.com/MVIG-SJTU/AlphaPose/blob/master/docs/INSTALL.md
    conda install pytorch==1.1.0 torchvision==0.3.0
    git clone https://github.com/MVIG-SJTU/AlphaPose.git
    cd AlphaPose
    export PATH=/usr/local/cuda/bin/:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda/lib64/:$LD_LIBRARY_PATH
    pip install cython
    conda install matplotlib
    vim setup.py  # delete lines 171 & 172, as suggested here: https://github.com/MVIG-SJTU/AlphaPose/issues/572
    conda install -c conda-forge pycocotools
    python3 setup.py build develop --user

Once installed, add the following to your .bashrc
    ALPHAPOSE_PATH=<absolute path of the AlphaPose directory>
  
Reload ~/.bashrc
    
    source ~/.bashrc

Download this repo if you haven't already

    git clone git@github.com:fairinternal/sketch_rig.git
    cd sketch_rig
  
There are a couple of files that need patching in alphapose. Run the following commands to do so:

    cp alphapose_patch_files/demo_inference.py ${ALPHAPOSE_PATH}/scripts/demo_inference.py
    cp alphapose_patch_files/bbox.py ${ALPHAPOSE_PATH}/alphapose/utils/bbox.py
    cp alphapose_patch_files/pPose_nms.py ${ALPHAPOSE_PATH}/alphapose/utils/pPose_nms.py


# Run

After setup has been completed, you can create a rigged character:

    ./run.sh ${INPUT_DIR} ${OUTPUT_DIR}  # INPUT_DIR a directory containg png image(s) with a drawn humanoid. OUTPUT_DIR is where the results will be saved

After this, the files needed for animation should be in ${OUTPUT_DIR}/animation_files
