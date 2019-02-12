'''
This file loads a pre-trained keras model, and export it to protobuff format
to be served with tensorflow serving.
'''

import tensorflow as tf
from tensorflow.keras.models import model_from_json

MODEL_PATH = '../model/model.json'
WEIGHT_PATH = '../model/model.h5'
EXPORT_PATH = '../model/exported/1'

# load model architecture from json
with  open(MODEL_PATH, 'r') as json_file:
    loaded_model_json = json_file.read()
model = model_from_json(loaded_model_json)
print('Model architecture loaded')

# load weights into new model
model.load_weights(WEIGHT_PATH)
print("Model weight loaded")

# export model

# Fetch the Keras session and save the model
# The signature definition is defined by the input and output tensors
# And stored with the default serving key
with tf.keras.backend.get_session() as sess:
    tf.saved_model.simple_save(
        sess,
        EXPORT_PATH,
        inputs={'input_image': model.input},
        outputs={t.name: t for t in model.outputs})

print('Model exported to' + EXPORT_PATH)
