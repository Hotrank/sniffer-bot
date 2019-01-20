# serialize model to JSON
model_json = model.to_json()
with open("../model/model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("../model/model.h5")
print("Saved model to disk")
