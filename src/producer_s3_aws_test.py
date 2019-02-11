import time
import zmq
import base64
import os
import boto3

BUCKET_NAME = 'drug-detector-images'

def producer():

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://*:5557")

    resource = boto3.resource('s3')
    my_bucket = resource.Bucket(BUCKET_NAME)
    files = list(my_bucket.objects.filter(Prefix = ''))

    zmq_socket.send_json({'url': 'start'})
    for file in files:
        url = BUCKET_NAME + '/' + file.key
        bytes = bytearray(file.get()['Body'].read())
        message = base64.b64encode(bytes)
        meta_data = { 'url' : url }
        zmq_socket.send_json(meta_data, flags=zmq.SNDMORE)
        zmq_socket.send(message)
    zmq_socket.send_json({'url': 'done'})
    print('All images sent. Total:', len(files))

if __name__ == "__main__":
    producer()
