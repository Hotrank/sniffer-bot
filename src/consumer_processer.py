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

DB_HOST = config['mysql']['db_host']
DB_PORT = config['mysql']['db_port']
DB_USER = config['mysql']['db_user']
DB_PASSWD = config['mysql']['db_passwd']
DB_NAME = config['mysql']['db_name']
PRODUCER_ADDRESS = config['zmq_producer']

N_WORKERS = 20
COMMIT_SIZE = 20


def worker(q):
    ''' for each image in the work queue, preprocess the image, send it to the
    prediction cluster, and write results to database.
    q: the work queue. Each item in the queue contains one image in bytes and
    its metadata in json'''
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
        if count == COMMIT_SIZE:
            mycursor.executemany(sql, val)
            mydb.commit()
            val = []
            count = 0
    if count > 0:
        mycursor.executemany(sql, val)
    mydb.commit()
    mycursor.close()
    mydb.close()

def enqueue_jobs(q):
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
    end = time()
    print('processing finished', end)
