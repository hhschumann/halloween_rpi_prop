#!/bin/bash

source /home/hschumann/halloween/venv/bin/activate

sudo pigpiod

python /home/hschumann/halloween/app.py
