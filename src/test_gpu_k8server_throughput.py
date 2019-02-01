import requests
from tensorflow.python.keras.applications.resnet50 import preprocess_input
from tensorflow.python.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import json
from time import time
import multiprocessing
import datetime
import MySQLdb
import subprocess
import os

MODEL_SERVER_URL = 'http://ab61c4f06265211e987ef0ee9a12caec-2038447575.us-east-1.elb.amazonaws.com:80/v1/models/drug_detector:predict'
test_dir = '../images/train/normal/'
image_size = 224
batch_size = 5



def read_and_prep_image(image_path, img_height=image_size, img_width=image_size):
    img = img_to_array(load_img(image_path, target_size=(image_size, image_size)))
    img_array = np.array(img)
    output = preprocess_input(img_array)
    return output


def worker(q):
    mydb = MySQLdb.connect(
      host="mysql-large.ccsroiuq1uw2.us-east-1.rds.amazonaws.com",
      port = 3306,
      user = "heming",
      passwd="xenia0427rds",
      db="mydb"
    )
    mycursor = mydb.cursor()

    count = 0
    inputs = []
    while not q.empty():
        image_path = q.get()
        input = read_and_prep_image(image_path)
        inputs.append({'input_image': input.tolist()})
        # flag = bool( np.argmin(json.loads(r.content.decode('utf-8'))['predictions'],1))
        # url = 'test_url'
        # date = datetime.datetime.today().strftime('%Y-%m-%d')
        # sql = "INSERT INTO images (url, path, process_date, flag) VALUES (%s, %s, %s, %s)"
        # val = (url, image_path, date, flag)
        # mycursor.execute(sql, val)
        count += 1
        if count == batch_size:
            payload =  { "instances": inputs}
            r = requests.post(MODEL_SERVER_URL, json=payload)
            inputs = []
            count == 0
            # mydb.commit()
    payload =  { "instances": inputs}
    r = requests.post(MODEL_SERVER_URL, json=payload)
    mydb.commit()
    mycursor.close()
    mydb.close()


def push_jobs(q, dir):
    fnames = os.listdir(dir)
    for fname in fnames:
        q.put(dir+fname)
    return len(fnames)



if __name__ == '__main__':
    n_workers = 2
    pQueue = multiprocessing.Queue()
    n_jobs = push_jobs(pQueue, test_dir)
    processes = []
    start = time()
    for _ in range(n_workers):
        process = multiprocessing.Process(target=worker, args=(pQueue,))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    total_time = time() - start
    print('number of workers:', n_workers)
    print ('time per images:', total_time/n_jobs)
