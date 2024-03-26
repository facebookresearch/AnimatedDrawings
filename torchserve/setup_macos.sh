# needed for torchserve
# if no java..
if ! command -v java &> /dev/null
then
	echo "java could not be found, installing"
	brew install java
	sudo ln -sfn /opt/homebrew/opt/openjdk/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk.jdk
fi

echo "*** Installing packages"
git clone https://github.com/jin-s13/xtcocoapi.git
cd xtcocoapi
pip install -r requirements.txt
python setup.py install
cd ..

pip install -U openmim torch==1.13.0 torchserve mmdet==2.27.0 mmpose==0.29.0 numpy==1.23.3 requests==2.31.0 scipy==1.10.0 tqdm==4.64.1
mim install mmcv-full==1.7.0

echo "*** Downloading models"
mkdir -p ./model-store
wget https://github.com/facebookresearch/AnimatedDrawings/releases/download/v0.0.1/drawn_humanoid_detector.mar -P ./model-store/
wget https://github.com/facebookresearch/AnimatedDrawings/releases/download/v0.0.1/drawn_humanoid_pose_estimator.mar -P ./model-store/

echo "*** Now run torchserve:"
echo "torchserve --start --ts-config config.local.properties --foreground"
