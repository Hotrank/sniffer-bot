This is a very high level instruction on how to setup and run the project.

#### Prerequisites
1. An [AWS account](https://aws.amazon.com/account/)
2. A pre-trained Keras (TensorFlow) model, or use the one in this repo.
3. Create a TF serving docker image following [the tensorflow serving instruction](tensorflow_serving_instructions.md)
4. Create a Kubernetes cluster on AWS and depoly the docker container as the "Prediction Cluster". See [the k8s instruction](kubernetes_instructions.md) for details.

#### System setup
1. Create an AWS EC2 instance as a "intake-server"
2. Create one or more AWS EC2 instance as "pre-processing server"
3. Create an AWS RDS MySQL database.

#### System Operation
1. Run consumer_processer.py on every "pre-processing server"
2. Run producer_from_local.py on the "intake-server" if the images are in the "intake-server", or run producer_from_s3.py if the images are stored in a S3 bucket.
