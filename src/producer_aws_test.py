import time
import zmq
import base64
import os
# producer
def producer():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://*:5557")
    # Need to Start conmusers before starting producers
    test_dir = '../../images/test/'
    fnames = os.listdir(test_dir)
    image_paths = [test_dir + fname for fname in fnames]
    zmq_socket.send_json({'url': 'start'})
    for i in range(len(image_paths)):
        with open(image_paths[i],'rb') as f:
            bytes = bytearray(f.read())
            message = base64.b64encode(bytes)
            meta_data = { 'url' : fnames[i] }
            zmq_socket.send_json(meta_data, flags=zmq.SNDMORE)
            zmq_socket.send(message)
    zmq_socket.send_json({'url': 'done'})
    print('all images sent. total jobs:', len(fnames))

producer()
