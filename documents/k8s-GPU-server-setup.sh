# follow this instruction to setup each GPU instance in the k8s cluster

# 1. install nvidia driver
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt update
sudo apt install nvidia-384
sudo reboot
nvidia-smi


# 2. install Docker: testing only, NO not do it for k8s instances
# following this post: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
apt-cache policy docker-ce
sudo apt-get install -y docker-ce

# test
sudo systemctl status docker


# 3. install Nvidia-docker2
# following this post: https://github.com/NVIDIA/nvidia-docker#quick-start
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
  sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update

# Install nvidia-docker2 and reload the Docker daemon configuration
# find the docker version
sudo docker version
# find the correct version of nvidia-docker and runtime
apt-cache madison nvidia-docker2 nvidia-container-runtime
# install using the correct versions
sudo apt-get install -y nvidia-docker2=2.0.3+docker17.03.2-1 nvidia-container-runtime=2.0.0+docker17.03.2-1
sudo pkill -SIGHUP dockerd

# Test nvidia-smi with the latest official CUDA image
docker run --runtime=nvidia --rm nvidia/cuda:9.0-base nvidia-smi

# make nviia default runtime
sudo nano /etc/docker/daemon.json

{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
# then reboot system.

# Now do the following on Local terminal, following this post:
# https://github.com/NVIDIA/k8s-device-plugin
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.11/nvidia-device-plugin.yml
