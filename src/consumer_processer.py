import requests
from tensorflow.python.keras.applications.resnet50 import preprocess_input
from tensorflow.python.keras.preprocessing.image import img_to_array
from PIL import Image as pil_image
import numpy as np
import json
from time import time
import multiprocessing
import datetime
import MySQLdb
import os
import io
import zmq
import base64

with open('config.json') as json_config_file:
    config = json.load(json_config_file)

MODEL_SERVER = config['model_server']

DB_HOST = config['mysql']['db_host']
DB_PORT = config['mysql']['db_port']
DB_USER = config['mysql']['db_user']
DB_PASSWD = config['mysql']['db_passwd']
DB_NAME = config['myswl']['db_name']
PRODUCER_ADDRESS = config['zmq_producer']

N_WORKERS = 20
COMMIT_SIZE = 20

image_size = 224

def load_bytes_img(bytes, grayscale=False, target_size=None):
    """Loads an image from byte array into PIL format.
    moddified from tf.python.keras.preprocessing.image.load_img
    """

    img = pil_image.open(io.BytesIO(bytes))
    if grayscale:
      if img.mode != 'L':
        img = img.convert('L')
    else:
      if img.mode != 'RGB':
        img = img.convert('RGB')
    if target_size:
      hw_tuple = (target_size[1], target_size[0])
      if img.size != hw_tuple:
        img = img.resize(hw_tuple)
    return img


def preprocess_img(image_bytes, image_size=image_size):
    ''' preprocess an image from bytes array to input form for resnet model'''
    img = img_to_array(load_bytes_img(image_bytes, target_size=(image_size, image_size)))
    img_array = np.array(img)
    output = preprocess_input(img_array)
    return output


def decode_response(r):
    ''' decode the prediction to True (drug) or False (not drug)'''
    scores = json.loads(r.content.decode('utf-8'))['predictions']
    return bool(np.argmin(scores, 1))



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
    processes.append(enqueue_process)
    for _ in range(N_WORKERS):
        process = multiprocessing.Process(target=worker, args=(pQueue,))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    end = time()
    print('processing finished', end)
