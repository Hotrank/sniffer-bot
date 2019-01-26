import requests
from tensorflow.python.keras.applications.resnet50 import preprocess_input
from tensorflow.python.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import json
from time import time

SERVER_URL = 'http://ad78303631f8111e9a4dc0ec68af0841-1388077874.us-east-1.elb.amazonaws.com:80/v1/models/drug_detector:predict'
image_path = '../images/test/drug_01.jpg'

image_size = 224

start = time()
for i in range(10):
    img = img_to_array(load_img(image_path, target_size=(image_size, image_size)))
    img_array = np.array(img)
    input = preprocess_input(img_array)
end = time()
process_time = end - start
print('preprocess time =', process_time/10 )

payload =  { "instances": [{'input_image': input.tolist()}]}

total_time = 0

for i in range(3):
    r = requests.post(SERVER_URL, json=payload)
    total_time += r.elapsed.total_seconds()
pred = json.loads(r.content.decode('utf-8'))
print('prediction is', pred)
print('prediction time =', total_time/3)
