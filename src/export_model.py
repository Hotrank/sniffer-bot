import tensorflow as tf
from tensorflow.keras.models import model_from_json

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

# export model
export_path = '../model/exported/1'

# Fetch the Keras session and save the model
# The signature definition is defined by the input and output tensors
# And stored with the default serving key
with tf.keras.backend.get_session() as sess:
    tf.saved_model.simple_save(
        sess,
        export_path,
        inputs={'input_image': model.input},
        outputs={t.name: t for t in model.outputs})

print('Model exported to' + export_path)
