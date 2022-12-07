from flask import request, Flask, render_template, jsonify
from werkzeug.utils import secure_filename
from collections import defaultdict
from threading import Lock
import requests
from gevent.pywsgi import WSGIServer
import os

mutex = Lock()


class Manager:
    # Initliaze
    job_id = 0
    worker_id = 0
    ip_list = defaultdict()
    workers = []

    def __init__(self):
        root = os.path.dirname(__file__)
        self.img_folder = os.path.join(root, 'images')
        if not os.path.exists(self.img_folder):
            os.makedirs(self.img_folder)

    def process_request(self, filename, jb_id):

        img = {'image': open('images/' + filename, 'rb')}

        while True:
            # If there is no worker node return 400 bad request
            if len(self.workers) == 0 and len(self.ip_list) == 0:
                print("No active worker node now")
                return "No Worker Node Active!", 400

            else:
                ip, wk_id = self.assign_job()
                print("Assigning Job " + str(jb_id) + " to Worker Node " + str(wk_id))

                if self.check(wk_id):
                    print("Job " + str(jb_id) + " has assigned to worker node " + str(wk_id))
                    request = requests.post(ip + "/", files=img)
                    self.workers.append(wk_id)
                    return request.json()['result']
                else:
                    print("Job " + str(jb_id) + " has failed to assign to worker node"+ str(wk_id))
                    return

    #get ip address and worker node id for new job
    def assign_job(self):
        worker_id = self.workers[0]
        ip = self.ip_list[worker_id]
        del self.workers[0]
        return ip, worker_id

    #check node connection
    def check(self, wk_id):
        try:
            result = requests.get(self.workers[wk_id] + "/status")
        except:
            print("Worker node " + str(wk_id) + " failed to connect")
            del self.workers[wk_id]
            return False
        if (result.status_code != 200):
            del self.workers[wk_id]
            return False
        else:
            return True

    def add_new(self, url):
        with mutex:
            wid = self.worker_id
            self.worker_id += 1
            self.ip_list[wid] = url
            self.workers.append(wid)
        return True

    def newjob(self):
        with mutex:
            jb_id = self.job_id
            self.job_id += 1
            return jb_id


# web servers
app = Flask(__name__)
manager = Manager()


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/', methods=['POST'])
def predict():
    # get new job id
    jobid = manager.newjob()
    # get image file
    img = request.files['file']
    newfilename = secure_filename("job-" + str(jobid) + "-" + img.filename)
    img_path = os.path.join(manager.img_folder, newfilename)
    img.save(img_path)
    r = manager.process_request(newfilename, jobid)

    return r


@app.route('/addnode', methods=['POST'])
def addnode():
    ip = request.remote_addr
    port = request.form['port']
    url = "http://" + ip + ":" + port
    if manager.add_new(url):
        return jsonify({'message': "Worker Added Successfully"})
    else:
        return jsonify({'message': "Worker Added Failed"}), 400


if __name__ == '__main__':
    http_server = WSGIServer(('127.0.0.1', 8080), app)
    http_server.serve_forever()
