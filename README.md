# CS655-Mini-Project


#### 3.1.1 Set up GENI

​	We only need two nodes for this project. One of them is for HTML file. We use Nginx to start a html server. Another one is server which will provide a machine learning service. The script to download Rspec files is wget https://raw.githubusercontent.com/zf990318/CS655-Mini-Project/master/rspec.txt
. When I started this project, I forgot to choose Publicly Routable Ip for the nodes which resulted in I can't visit the nodes even the service was started successfully.Make sure you choose the "Publicly Routable IP" option

SSH to web interface node using:

ssh -i ~/.ssh/id_geni_ssh_rsa yiyinghu@pcvm3-28.instageni.research.umich.edu -p 22

SSH to ML-server node using:

ssh -i ~/.ssh/id_geni_ssh_rsa yiyinghu@pcvm3-29.instageni.research.umich.edu -p 22


#### 3.1.2 Set up HTML-Server

​	The html server is actually the client for this project. We chose tp deploy the html on Nginx. SSH to HTML-Server node

​	**Step 1: Install Nginx**

```
sudo apt update
sudo apt install nginx
```

 	Step 2: Adjust the firewall to allow the Nginx service to pass through

```
sudo ufw app list
sudo ufw allow 'Nginx HTTP'
sudo ufw allow 'Nginx HTTPS'
```

​	Step 3: Make Sure the Nginx is running

```
systemctl status nginx
```

​	Nginx is running succesfully if you see

```
● nginx.service - A high performance web server and a reverse proxy server
```

Type in the ip of your node in browser, ip of my http-server is 192.41.233.48

Nginx works succesfully if you see this page

​	Step 4: Edit **/etc/nginx/sites-available** 

```
root /users/yiyinghu/HTML/templates;
index index.html
```

​	Step 5: Restart Nginx

```
sudo nginx -s reload
```

Now, when I type in the ip of html server, I am able to see my own page



#### 3.1.3 Set up ML-Server

As we need do some prediction based on machine learning. So we use Python to do the back-end. 

Step1: Install Anaconda3

```
wget https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh

```

Step2: Set up Environment

Edit /.bashrc

```
export PATH=/users/yiyinghu/anaconda3/bin:$PATH
```

Create virtual environment and activate 

```
conda create -n CS655 python=3.7
conda activate CS655 
```

Download packages

Run server

```
python3 ML-Server.py
'''
The server will running at 192.41.233.48:5000
