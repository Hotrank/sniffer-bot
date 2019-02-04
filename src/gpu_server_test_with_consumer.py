import requests
from tensorflow.python.keras.applications.resnet50 import preprocess_input
from tensorflow.python.keras.preprocessing.image import img_to_array
import numpy as np
import json
from time import time
import multiprocessing
import datetime
import MySQLdb
import os
import io
from PIL import Image as pil_image
import zmq
import base64


model_server = 'http://ae519c526270011e987ef0ee9a12caec-650811435.us-east-1.elb.amazonaws.com:80/v1/models/drug_detector:predict'
image_size = 224
commit_size = 20
db_host= "mysql-large.ccsroiuq1uw2.us-east-1.rds.amazonaws.com"
db_port = 3306
db_user = "heming"
db_passwd="xenia0427rds"
db_name="mydb"
intake_server = "tcp://10.0.0.13:5557"
job_count = 0
start, end = 0, 0

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
        host = db_host,
        port = db_port,
        user = db_user,
        passwd= db_passwd,
        db= db_name
        )
    mycursor = mydb.cursor()

    count = 0
    val = []
    sql = "INSERT INTO images (url, process_date, path, flag) VALUES (%s, %s, %s, %s)"
    path = 'fake_path'
    while True:
        try:
            url, image_bytes = q.get(block=True, timeout = 5)
        except:
            break
        if url == 'start':
            global start
            start = time()
            print('start processing... please start producer in 5 seconds', start)
            continue
        if url == 'done':
            break
        input = preprocess_img(image_bytes)
        payload =  { "instances": [{'input_image': input.tolist()}]}
        r = requests.post(model_server, json=payload)
        flag = decode_response(r)
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        val.append((url, date, path, flag))
        count += 1
        if count == commit_size:
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
    receiver.connect(intake_server)

    while True:
        meta_data = receiver.recv_json()
        url = meta_data['url']
        if url == 'start':
            q.put(('start', None))
            continue
        if url == 'done':
            q.put(('done', None))
            print ('all jobs queued.')
            break
        message = receiver.recv()
        image_bytes = bytearray(base64.b64decode(message))
        item = (url, image_bytes)
        q.put(item)
        global job_count
        job_count += 1
    print('total job:', job_count)


if __name__ == '__main__':
    n_workers = 20
    pQueue = multiprocessing.Queue()
    processes = []
    enqueue_jobs(pQueue)
    for _ in range(n_workers):
        process = multiprocessing.Process(target=worker, args=(pQueue,))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    end = time()
    print('processing finished', end)
    if start>0:
        print('total time', end-start )
    print('number of workers:', n_workers)
