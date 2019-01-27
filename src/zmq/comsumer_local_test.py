import time
import zmq
import random


# consumer
def consumer():
    consumer_id = random.randrange(1,10005)
    print ('I am consumer {}'.format(consumer_id))
    context = zmq.Context()
    # recieve work
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://127.0.0.1:5557")

    while True:
        work = consumer_receiver.recv_json()
        data = work['num']
        print(data)

consumer()
