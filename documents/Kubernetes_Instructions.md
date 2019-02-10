Follow See [this tutorial](https://ramhiser.com/post/2018-05-20-setting-up-a-kubernetes-cluster-on-aws-in-5-minutes/) to set up a kubernetes cluster.

#### Prerequisites
1. Create an AWS account and install the AWS Command Line Interface:  
```
pip install awscli --upgrade --user
```  
2. Configure your AWS CLI with your credential: `aws configure`

3. Install kubectl and kops:  
```
curl -LO https://github.com/kubernetes/kops/releases/download/$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d '"' -f 4)/kops-linux-amd64
chmod +x kops-linux-amd64
sudo mv kops-linux-amd64 /usr/local/bin/kops
```  
```
sudo apt-get update && sudo apt-get install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl
```  
4. create an S3 bucket to store the cluster state.

#### Setting up the k8s cluster

1. Setup the environmental variables  
```
export KOPS_CLUSTER_NAME=heming-gpu.k8s.local
export KOPS_STATE_STORE=s3://kops-state-heming
```  
2. Generate the cluster configuration  
```
kops create cluster --node-count=2 --node-size=p2.xlarge --zones=us-east-1b --master-size=m4.large
```
The default OS for the instances is Amazon Unix, you can edit the configuration to use different Amazon Machine Images(AMI). First find the AMI ID for the operating system image on the AWS website. Then use command ```aws ec2 describe-images --image-id <image_ID>``` to find the image location. Finally edit the image specification in the cluster setup ```kops edit ig --name=heming-gpu.k8s.local nodes```

3. Spin up the cluster
```
kops update cluster --name ${KOPS_CLUSTER_NAME} --yes
```
This may take a few minutes. Use the following command to check the status.
```
kops validate cluster
```

#### Deploy the Model
1. Create a Deployment to run the model container
```
kubectl create -f deployment-gpu.yml
```  
2. Create a Load Balancer Service to expose the deployment  
```
kubectl apply -f deployment.yml
```
To find the LoadBalancer ingress, use
```
kubectl describe service
```

#### Setup for GPU instance [optional]
If deploying TensorFlow on GPU, each node in the k8s cluster needs to be a GPU instance. After the cluster is up, ssh into each node instance and install the Nvidia driver and Nvidia-Docker2

1. Install Nvidia driver
```
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt update
sudo apt install nvidia-384
sudo reboot
nvidia-smi
```

2. Install Nvidia-Docker2  
```
# Update apt source list
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
  sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
```
```
# check Docker version
sudo docker version
```
```
# find the versions of nvidia-docker and runtime that's compatible with docker version
apt-cache madison nvidia-docker2 nvidia-container-runtime
```
```
# install using the correct versions
sudo apt-get install -y nvidia-docker2=2.0.3+docker17.03.2-1 nvidia-container-runtime=2.0.0+docker17.03.2-1
sudo pkill -SIGHUP dockerd
```
