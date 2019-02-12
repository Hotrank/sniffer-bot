This document shows how to create a tensorflow serving docker image with your pre-trained model.

#### Prerequisites
1. Export model for serving  
Modify and run export_model.py to load your saved keras model, and save it to protobuff format for serving.  
2. Install Docker (see [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04))
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce
```

#### Create TF serving docker image with your exported model
1. pull and run the official tensorflow docker image (I used the GPU version)
```
sudo docker pull tensorflow/serving:latest-gpu
sudo docker run -d --name serving_base tensorflow/serving:latest-gpu
```
2. copy your model into the docker container and commit.
```
sudo docker cp /home/ubuntu/drug_detect/model/exported serving_base:models/drug_detector
sudo docker commit --change "ENV MODEL_NAME drug_detector" serving_base heming/drug-detector-gpu
```
3. upload your model to docker hub
```
sudo docker login --username=<your_user_name>
sudo docker tag <image_ID> <your_user_name>/<your_image_name>:latest
sudo docker push <your_user_name>/<your_image_name>
```
