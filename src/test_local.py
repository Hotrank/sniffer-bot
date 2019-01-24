from tensorflow.python.keras.applications.resnet50 import preprocess_input
import os
from os.path import join
import numpy as np
from tensorflow.python.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import model_from_json
from time import time

model_path = '../model/model.json'
weight_path = '../model/model.h5'

# load model architecture from json
with  open(model_path, 'r') as json_file:
    loaded_model_json = json_file.read()
model = model_from_json(loaded_model_json)
print('Model architecture loaded')

# load weights into new model
model.load_weights(weight_path)
print("Model weight loaded")

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
input = input.reshape((1, image_size, image_size, -1))

start = time()
pred = model.predict(input)
end = time()
print('prediction time = ', end - start)
