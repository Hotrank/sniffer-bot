# Prerequisites: docker, git
# Additional reqcuirements for GPU: Nvidia driver, nvidia-docker2

git clone https://github.com/Hotrank/drug_detect.git
sudo docker pull tensorflow/serving:latest-gpu
sudo docker run -d --name serving_base_1 tensorflow/serving:latest-gpu
sudo docker cp /home/ubuntu/drug_detect/model/exported serving_base_1:models/drug_detector
sudo docker commit --change "ENV MODEL_NAME drug_detector" serving_base_1 heming/drug-detector-gpu

# push the image to docker hub
# go to dockerhub website, create a new repository:
# mine called hotrank/drug-detector-gpu
sudo docker login --username=hotrank
sudo docker tag f5f5c90312a7 hotrank/drug-detector-gpu:latest
sudo docker push hotrank/drug-detector-gpu
