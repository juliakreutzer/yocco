import io
import json
import os

from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
from flask import Flask, jsonify, request, render_template, redirect
from .utils import load_classes

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
imagenet_class_index = json.load(open('app/imagenet_class_index.json'))
model = models.densenet121(pretrained=True)
class_dict = load_classes('app/static/garbage/')
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
    temp_file = "app/static/temp/upload.jpg"
    if request.method == 'POST':
        file = request.files['file']
        img_bytes = file.read()
        with open(temp_file, mode="wb") as jpg:
            jpg.write(img_bytes)
        class_id, class_name = get_prediction(image_bytes=img_bytes)
        garbage_type, co = garbage_class(class_name)
        return render_template('result.html',
                               class_name=class_name,
                               garbage_type=garbage_type,
                               co=co)
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

