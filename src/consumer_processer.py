'''
This is the main file to run on each of the preprocessing server.
It starts a zmq consumer that takes images from the producer (on another instance),
and put them into a multiprocessing queue.
Multiple processes will run to take images from the queue, preprocess them,
send the preprocessed image to the k8s cluster for prediction, and save the
predictions to a MySQL database in batches.
'''

import requests
import json
from time import time
import multiprocessing
import datetime
import MySQLdb
import zmq
import base64
from utils import preprocess_img, decode_response


with open('config.json') as json_config_file:
    config = json.load(json_config_file)

MODEL_SERVER = config['model_server']
PRODUCER_ADDRESS = config['zmq_producer']
DB_HOST = config['mysql']['db_host']
DB_PORT = config['mysql']['db_port']
DB_USER = config['mysql']['db_user']
DB_PASSWD = config['mysql']['db_passwd']
DB_NAME = config['mysql']['db_name']

# number of processes to run in parallel, should be slightly above the number
# of CPU cores.
N_WORKERS = 20

# batch size to perform a database write&commit
COMMIT_SIZE = 20


def worker(q):
    '''
    q: a multiprocessing.Queue object. Each item in the queue contains a tuple
    of url, image_bytes)

    a worker continously take images from the work queue, preprocess the image,
    send it to the prediction cluster, and write results to database in batches.
    '''

    mydb = MySQLdb.connect(
        host = DB_HOST,
        port = DB_PORT,
        user = DB_USER,
        passwd= DB_PASSWD,
        db= DB_NAME
        )
    mycursor = mydb.cursor()

    count = 0
    val = []
    sql = "INSERT INTO images (url, process_date, flag) VALUES (%s, %s, %s)"

    while True:
        # block=True: no exception will be thrown when queue is empty
        # timeout = 5 : timeout expection will be thrown after 5 seconds
        try:
            url, image_bytes = q.get(block=True, timeout = 5)
        except:
            break
        if url == 'start':
            print('start processing at', time())
            continue
        if url == 'done':
            break

        input = preprocess_img(image_bytes)
        payload =  { "instances": [{'input_image': input.tolist()}]}
        r = requests.post(MODEL_SERVER, json=payload)
        flag = decode_response(r)
        process_date = datetime.datetime.today().strftime('%Y-%m-%d')
        val.append((url, process_date, flag))
        count += 1

        # save and commit to database after COMMIT_SIZE records are accumulated
        if count == COMMIT_SIZE:
            mycursor.executemany(sql, val)
            mydb.commit()
            val = []
            count = 0

    # save and commit the remaining records before closing connection
    if count > 0:
        mycursor.executemany(sql, val)
    mydb.commit()
    mycursor.close()
    mydb.close()

def enqueue_jobs(q):
    '''
    q: a multiprocessing.Queue object. Each item in the queue contains a tuple
    of url, image_bytes)

    This function starts a zmq consumer which take images with metadata from a
    zmq producer, and put them into the queue.
    '''


    context = zmq.Context()
    receiver = context.socket(zmq.PULL)
    receiver.connect(PRODUCER_ADDRESS)

    while True:
        meta_data = receiver.recv_json()
        url = meta_data['url']
        if url == 'start':
            q.put(('start', None))
            continue
        if url == 'done':
            # TODO: put send finish signal to queue n_worker times
            print ('all jobs queued.')
            break
        message = receiver.recv()
        image_bytes = bytearray(base64.b64decode(message))
        item = (url, image_bytes)
        q.put(item)


if __name__ == '__main__':
    pQueue = multiprocessing.Queue()
    processes = []
    enqueue_process = multiprocessing.Process(target=enqueue_jobs, args=(pQueue,))
    enqueue_process.start()
    processes.append(enqueue_process)
    for _ in range(N_WORKERS):
        process = multiprocessing.Process(target=worker, args=(pQueue,))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    print('processing finished', time())
