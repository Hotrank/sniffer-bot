# sniffer-bot: Insight Data Engineer Project 2019A

Social media platforms is bringing us closer than over. However it can be used for unintended purpose - selling illegal drugs (see this Washington Post article). For sniffer-bot project, I trained a image classification model to identify certain drug images, deployed it in a Tensorflow docker container, and scaled it up on a Kubernetes GPU cluster on AWS.

### Prepare a image Classification Model
The model was trained with Keras (Tensorflow backend) using transfer learning based on Resnet50. Essentially the last layer of Resnet50 was replaced by a binary softmax, and the corresponding weights re-trained for drug image classification.


The model was then exported to protobuff format and integrated into the official tensorflow serving container, which exposes a REST API for inference. See the official guide for how to export your model and customize the official container with your own model for serving.

### Deploy the model with Kubernets on AWS
Kubernetes(k8s) is a portable, extensible open-source platform for managing containerized workloads and services. There are several ways to use k8s on AWS. A popular method is to use kops to spin up a k8s cluster. See this tutorial on how to do that.

After the k8s cluster is up and running, "deployment" and "service" can be launched using their corresponding yml files. A "deployment" specifies the container(s) and its number of replicas to be deployed, while the "service" exposes the deployment with a load balancer that's accessible from outside of the 8ks cluster.

### Complete project framework
ZeroMQ(zmq) was used to generate a stream of images from an S3 bucket. Multiple CPU instances will consume these images, send them to the k8s cluster for inference, and save the prediction to a MySQL database. See the diagram illustration below.
