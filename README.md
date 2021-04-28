# sketch_rig

This is the first of the two repos that comprise the Animating Children's Sketches project. This repo contains the code necessary to detect humanoid characters within a drawing, segment them from the background, and predict joint locations onto the character.

The output of the process is a set of image files and a .YAML file that can be animated using the sketch_animate repo.





Step 1 - 
# Download the Detectron2 weights and add the following to .bashrc
DETECTRON2_WEIGHTS_LOC=<absolute path of detectron2 weights>

# Download the Alphapose weights and add the following to .bashrc
ALPHAPOSE_WEIGHTS_LOC=<absolute path of alphapose weights>

#Chose names for your detectron2 and alphapose virtual envs and add this to your .bash_rc file
D2_VIRTUAL_ENV_NAME=<a name for your detectron2 conda virtualenv>
AP_VIRTUAL_ENV_NAME=<a name for your alphapose conda virtualenv>

source ~/.bashrc

#Next, install Detectron2 on your machine. This is how I installed it on the FAIR cluster
module load cuda/10.2
conda create  --name ${D2_VIRTUAL_ENV_NAME} python=3.7.9
conda activate ${D2_VIRTUAL_ENV_NAME}
conda install opencv
conda install pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch
python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
conda install scikit-image
conda install scikit-learn
conda deactivate

#Next, install Alphapose on your machine. This is how I installed it on the FAIR cluster
conda create  --name ${AP_VIRTUAL_ENV_NAME} python=3.6 -y
conda activate ${AP_VIRTUAL_ENV_NAME}
# following is from here: https://github.com/MVIG-SJTU/AlphaPose/blob/master/docs/INSTALL.md
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

# Once installed, add the following to your .bashrc
ALPHAPOSE_PATH=<absolute path of the AlphaPose directory>

# There are a couple of files that need patching in alphapose. Run the following commands to do so:
cp alphapose_patch_files/demo_inference.py ${ALPHAPOSE_PATH}/scripts/demo_inference.py
cp alphapose_patch_files/bbox.py ${ALPHAPOSE_PATH}/alphapose/utils/bbox.py
cp alphapose_patch_files/pPose_nms.py ${ALPHAPOSE_PATH}/alphapose/utils/pPose_nms.py


## Run
To create a rigged character, run the follow script

./run.sh ${INPUT_DIR} ${OUTPUT_DIR}  # INPUT_DIR a file containg a png image with a drawn humanoid. OUTPUT_DIR is where the results will be saved

After this, the files needed for animation should be in ${OUTPUT_DIR}/animation_files
