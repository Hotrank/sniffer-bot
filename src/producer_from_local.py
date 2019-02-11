import zmq
import base64
import os


SOURCE_DIR = '../../test_images/'

def producer():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://*:5557")
    fnames = os.listdir(SOURCE_DIR)
    image_paths = [SOURCE_DIR + fname for fname in fnames]

    zmq_socket.send_json({'url': 'start'})
    for i, image_path in numerate(image_paths):
        with open(image_path,'rb') as f:
            bytes = bytearray(f.read())
            message = base64.b64encode(bytes)
            meta_data = { 'url' : image_path }
            zmq_socket.send_json(meta_data, flags=zmq.SNDMORE)
            zmq_socket.send(message)
    zmq_socket.send_json({'url': 'done'})
    print('All images sent. total:', len(fnames))

if __name__ == '__main__':
    producer()
