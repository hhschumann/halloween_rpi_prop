#!/bin/bash

sudo apt update
sudo apt install vim
sudo apt -y install python3-picamera2

python -m venv --system-site-packages venv
source venv/bin/activate python

pip install -r requirements.txt

yolo export model=yolo8n.pt format=ncnn 

deactivate
