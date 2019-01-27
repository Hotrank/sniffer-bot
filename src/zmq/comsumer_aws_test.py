import time
import zmq


# consumer
def consumer():
    context = zmq.Context()
    # recieve work
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://10.0.0.13:5557")

    while True:
        work = consumer_receiver.recv_json()
        data = work['num']
        print(data)

consumer()
