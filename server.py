from __future__ import division, print_function
import requests
from PIL import Image
from torchvision import transforms
from werkzeug.utils import secure_filename
from flask import request, Flask
from flask_cors import CORS
import torch.nn as nn
from torchvision.models import resnet50
import numpy as np
import asyncio



class Model():
    def __init__(self, inputPath):

        self.model = resnet50(pretrained = True).eval()

        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean = [0.485, 0.456, 0.406],
                std = [0.229, 0.224, 0.225]
            )
        ])
        self.path = inputPath
        self.label_url = "https://s3.amazonaws.com/mlpipes/pytorch-quick-start/labels.json"
        self.labels = {int(key):value for (key, value) in requests.get(self.label_url).json().items()}

        self.softmax = nn.Softmax(dim = 1)

    def loadImage(self, path):
        img = Image.open(path)
        image_tensor = self.preprocess(img)
        image_tensor.unsqueeze_(0)



    def predict(self):
        img = Image.open(self.path)
        image_tensor = self.preprocess(img)
        image_tensor.unsqueeze_(0)
        output = self.model(image_tensor)
        predict_output = self.softmax(output)
        idx = np.argsort(predict_output[0].data.numpy())[-1]
        category = str(self.labels[idx])
        score = str((predict_output[0].data.numpy()[idx])*100)

        result = "Predict Category: "+ category + ", Confidence Level: " + score+"%"

        return result


app = Flask(__name__)
loop = asyncio.get_event_loop()
CORS(app, resource=r'/*')
@app.route('/result', methods=['POST'])
def predict():
    if request.method == 'POST':

        img_file = request.files['image']
        img_file.save(secure_filename(img_file.filename))
        result = Model(secure_filename(img_file.filename)).predict()
        return result



if __name__ == '__main__':
    app.run(debug="true",host="0.0.0.0")
