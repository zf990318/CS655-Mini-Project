from __future__ import division, print_function
import os
import numpy as np
import requests
from PIL import Image
import torch.nn.functional as F
from torchvision import models, transforms
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
from flask import request, Flask, render_template
import time


result = ""

#Data pre-process
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225])
])
# Gett labels for image classification
LABELS_URL = 'https://s3.amazonaws.com/mlpipes/pytorch-quick-start/labels.json'
labels = {int(key):value for (key, value)
          in requests.get(LABELS_URL).json().items()}


# Set vgg16 pretrained model
model = models.vgg16(pretrained=True).eval()


app = Flask(__name__)
@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Record start time
        start_time = time.time()
        #recived image file
        file = request.files['image']

        # Save the file
        root = os.path.dirname(__file__)
        img_folder = os.path.join(root, 'images')
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)

        img_path = os.path.join(img_folder, secure_filename(file.filename))
        file.save(img_path)

        # Recognize the image
        img_pil = Image.open(img_path).convert("RGB")
        img_tensor = preprocess(img_pil)
        img_tensor.unsqueeze_(0)
        fc_out = model(img_tensor)
        fc_out = F.softmax(fc_out)
        lbl_out = np.argsort(fc_out[0].data.numpy())[-1]
        end_time = time.time()
        result = " Predict Result: " + str(labels[lbl_out]) + ",  Confidence: " + str((fc_out[0].data.numpy()[lbl_out])) + ",  Response Time: " + str((end_time - start_time))
        return result
    else:
        return None


if __name__ == '__main__':
    http_server = WSGIServer(('127.0.0.1', 8081), app)
    http_server.serve_forever()
