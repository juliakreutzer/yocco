import io
import json
import os
import numpy as np
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
from flask import Flask, jsonify, request, render_template, redirect
from .utils import load_classes
from keras.preprocessing.image import img_to_array
from keras.applications.mobilenet import decode_predictions, preprocess_input
from keras.preprocessing.image import load_img
from keras.models import load_model
import tensorflow as tf

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
imagenet_class_index = json.load(open('imagenet_class_index.json'))
waste_types = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
global waste_model
waste_model = load_model('hack_mobilenet.h5')
global graph
graph = tf.get_default_graph()
model = models.densenet121(pretrained=True)
class_dict = load_classes('static/garbage/')
model.eval()


def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)


def get_prediction(image_bytes):
    tensor = transform_image(image_bytes=image_bytes)
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    return imagenet_class_index[predicted_idx]


def garbage_class(class_name):
    """
    Classify an ImageNet category into 4 garbage classes and get CO2 mass.
    Example 'plastic_bag' -> 'recycle', '0.4'

    :param class_name: ImageNet class name.
    :return:
        Garbage class message.
        CO2 mass, also string.
    """
    normalized = class_name.split(',')[0].lower()
    for c, v in class_dict.items():
        for o, co in v:
            if normalized == o:
                message = c
                if c == 'compost':
                    message += ', check if still edible first'
                return message, co
    return "No garbage, detected a {}".format(normalized.replace('_', ' ')), "?"


@app.route('/', methods=['POST', 'GET'])
def predict():
    # TODO ugly handling of temp files.
    temp_file = "static/temp/upload.jpg"
    if request.method == 'POST':
        file = request.files['file']
        img_bytes = file.read()
        with open(temp_file, mode="wb") as jpg:
            jpg.write(img_bytes)
        # ImageNet prediction
        class_id, class_name = get_prediction(image_bytes=img_bytes)
        garbage_type, co = garbage_class(class_name)
        # Waste model prediction
        img = load_img(temp_file, target_size=(224, 224))
        #img = img_to_array(img) / 255.
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)
        with graph.as_default():
            waste_model._make_predict_function()
            waste_pred = waste_model.predict(img)[0]
        index = np.argmax(waste_pred)
        waste_label = waste_types[index]
        accuracy = "{0:.2f}".format(waste_pred[index] * 100)

        return render_template('result.html',
                               class_name=class_name,
                               garbage_type=garbage_type,
                               co=co, waste_label=waste_label,
                               waste_acc=accuracy)

    if os.path.exists(temp_file):
        os.remove(temp_file)  # this deletes the file

    return render_template('index.html')


# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


if __name__ == '__main__':
    app.run()

