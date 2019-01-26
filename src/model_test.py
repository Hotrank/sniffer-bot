from tensorflow.python.keras.applications import ResNet50
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Flatten, GlobalAveragePooling2D
from tensorflow.python.keras.applications.resnet50 import preprocess_input
import os
from os.path import join
import numpy as np
from tensorflow.python.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import model_from_json
from time import time

model_path = '../model/model.json'
weight_path = '../model/model.h5'

# load json and create model
with  open(model_path, 'r') as json_file:
    loaded_model_json = json_file.read()
model = model_from_json(loaded_model_json)
print('Model architecture loaded')

# load weights into new model
model.load_weights(weight_path)
print("Model weight loaded")

# test model accuracy
test_dir = '../images/test/'
fnames = os.listdir(test_dir)
image_paths = [test_dir + fname for fname in fnames]
labels = list(map(lambda x: 0 if x.startswith('drug') else 1, fnames))
n_files = len(labels)

image_size = 224
def read_and_prep_images(img_paths, img_height=image_size, img_width=image_size):
    imgs = [load_img(img_path, target_size=(img_height, img_width)) for img_path in img_paths]
    img_array = np.array([img_to_array(img) for img in imgs])
    output = preprocess_input(img_array)
    return(output)

test_data = read_and_prep_images(image_paths)

start = time()
preds = model.predict(test_data)
end = time()
print('prediction time is:', (end - start)/n_files)

acc = np.mean(preds == labels)
print('accuracy is {:.3f}'.format(acc))
