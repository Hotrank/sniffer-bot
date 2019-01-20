from tensorflow.python.keras.applications import ResNet50
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Flatten, GlobalAveragePooling2D


num_classes = 2
resnet_weights_path = '../model/resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5'
model = Sequential()
model.add(ResNet50(include_top = False, pooling = 'avg', weights = resnet_weights_path))
model.add(Dense(num_classes, activation = 'softmax'))

model.layers[0].trainable = False

model.compile(optimizer = 'sgd', loss='categorical_crossentropy', metrics=['accuracy'])

from tensorflow.python.keras.applications.resnet50 import preprocess_input
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator

image_size = 224
data_generator = ImageDataGenerator(
                                    preprocessing_function=preprocess_input,
                                    featurewise_center=False,
                                    horizontal_flip = True,
                                    rotation_range = 10

                                    )

train_generator = data_generator.flow_from_directory(
       directory = '../images/train',
       target_size=(image_size, image_size),
       batch_size= 10,
       class_mode='categorical')

validation_generator = data_generator.flow_from_directory(
       directory = '../images/val',
       target_size=(image_size, image_size),
       class_mode='categorical')

model.fit_generator(
       train_generator,
       steps_per_epoch= 25,
       epochs = 10,
       validation_data= validation_generator,
       validation_steps=1)


from os.path import join

test_dir = '../images/test/'
image_fnames_drug = ['drug_{:0>2d}.jpg'.format(i) for i in range(1,12)]
image_fnames_normal = ['normal_{:0>2d}.jpg'.format(i) for i in range(1,16)]
image_fnames = image_fnames_drug + image_fnames_normal
image_paths = [test_dir + fname for fname in image_fnames]



import numpy as np
from tensorflow.python.keras.preprocessing.image import load_img, img_to_array

def read_and_prep_images(img_paths, img_height=image_size, img_width=image_size):
    imgs = [load_img(img_path, target_size=(img_height, img_width)) for img_path in img_paths]
    img_array = np.array([img_to_array(img) for img in imgs])
    output = preprocess_input(img_array)
    return(output)


# In[12]:


test_data = read_and_prep_images(image_paths)
preds = np.argmax(model.predict(test_data),1)


# In[13]:


# from matplotlib import pyplot as plt
# get_ipython().run_line_magic('matplotlib', 'inline')
# labels = ['drug', 'normal']
#
# plt.figure(figsize=(30,60))
# for i in range(26):
#     ax = plt.subplot(7,4,i+1)
#     img = load_img(image_paths[i], target_size=(image_size, image_size))
#     array = np.array(img_to_array(img))/255
#     plt.imshow(array)
#     ax.axis('off')
#     ax.set_title('prediction:{}'.format(labels[preds[i]]))





# In[14]:


truth = [0]*11 + [1]* 15
acc = np.mean(preds == truth)
print('Model accuracy : {:.3f}'.format(acc))

# serialize model to JSON
model_json = model.to_json()
with open("../model/model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("../model/model.h5")
print("Saved model to disk")
