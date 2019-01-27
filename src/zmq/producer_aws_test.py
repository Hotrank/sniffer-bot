import time
import zmq

# producer
def producer():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://127.0.0.1:5557")
    # Need to Start conmusers before starting producers
    for num in range(10):
        work_message = { 'num' : num }
        time.sleep(1)
        zmq_socket.send_json(work_message)

producer()
