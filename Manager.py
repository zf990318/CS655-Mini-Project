from flask import request, Flask, render_template, jsonify
from werkzeug.utils import secure_filename
from collections import defaultdict
from threading import Lock
import requests
import time
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

    def processJob(self, filename, jb_id):

        img = {'image': open('images/' + filename, 'rb')}

        while True:
            # If there is no worker node return 400 bad request
            if len(self.workers) == 0 and len(self.ip_list) == 0:
                print("No active worker node now")
                return "Service Error: No Worker Node!", 400

            else:
                ip, wk_id = self.assignJob()
                print("Assigning Job " + str(jb_id) + " to Worker Node " + str(wk_id))

                if self.checkAlive(wk_id):
                    print(f"Successfuly Assigned Job: {jb_id} to Worker:{wk_id}")
                    try:
                        r = requests.post(ip + "/predict", files=img)
                    except:
                        # worker failed during processing, reassign job
                        print(f"Worker {wk_id} Connect Failed, Re-Assign Job {jb_id}")
                        self.removeworker(wk_id)
                        continue

                    self.ava_worker.append(wk_id)
                    return r.json()['result']
                else:
                    print(f"Failed to Assigned Job {jb_id} to Worker {wk_id}")

    def assignJob(self):
        worker_id = self.workers[0]
        ip = self.ip_list[worker_id]
        del self.workers[0]
        return ip, worker_id

    def checkAlive(self, wk_id):
        try:
            result = requests.get(self.workers[wk_id] + "/status")
        except:
            print(f"Worker {wk_id} Connect Failed")
            self.removeworker(wk_id)
            return False
        if (result.status_code == 200):
            return True
        else:
            self.removeworker(wk_id)
            return False

    def addworker(self, url):
        with mutex:
            wid = self.worker_id
            time.sleep(0.001)
            self.worker_id += 1
            self.ip_list[wid] = url
            self.workers.append(wid)

        print(f"Added Worker {wid} address: {url}")

        return True

    def removeworker(self, wid):
        del self.workers[wid]
        print(f"Removed Worker {wid}")

    def newjob(self):
        with mutex:
            jid = self.job_id
            time.sleep(0.001)
            self.job_id += 1
            return jid


# web servers
app = Flask(__name__)
manager = Manager()


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def upload():
    # get job id
    jobid = manager.newjob()
    # get file
    img = request.files['file']
    # save the file
    newfilename = secure_filename("job-" + str(jobid) + "-" + img.filename)
    img_path = os.path.join(manager.img_folder, newfilename)
    img.save(img_path)
    print(f"Saving File... id: {jobid}")

    r = manager.processJob(newfilename, jobid)
    # print(f"Predict Result: {r.json()['result']}")
    print(f"Job {jobid} Finished")

    return r


@app.route('/addnode', methods=['POST'])
def addnode():
    ip = request.remote_addr
    # print(request.form['port'])
    port = request.form['port']
    url = "http://" + ip + ":" + port
    if (manager.addworker(url)):
        return jsonify({'message': "Worker Added Successfully"})
    else:
        return jsonify({'message': "Worker Added Failed"}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="80")
