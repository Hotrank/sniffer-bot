from tensorflow.python.keras.applications.resnet50 import preprocess_input
from tensorflow.python.keras.preprocessing.image import img_to_array
from PIL import Image as pil_image
import numpy as np
import io
import json

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
