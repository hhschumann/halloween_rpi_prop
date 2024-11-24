import numpy as np
import cv2
import sys
import datetime
from ultralytics import YOLO
import math

from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
factory = PiGPIOFactory()

from picamera2 import Picamera2
from time import sleep

# Initialize the servo on GPIO pin 14
# min_pulse_width and max_pulse_width may need to be adjusted for your servo
servo = AngularServo(14, pin_factory=factory, initial_angle=90,  min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

model = YOLO("/home/hschumann/halloween/yolov8n_ncnn_model")

CLASS_NAMES = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush", "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush",
              ]

# Function to set the servo angle
def set_angle(angle):
    servo.angle = angle
    
def set_angle_slow(current_angle, new_angle):
    diff = new_angle-current_angle
    if diff > 0:
        for inc in range(1, diff+1):
            servo.angle=current_angle + inc
            sleep(0.01)
    if diff < 0:
        for inc in range(-1, diff-1, -1):
            servo.angle=current_angle + inc
            sleep(0.01)

def main():
    print('JACK-O\'-LANTERN ALIVE!')
    print(datetime.datetime.now())
    min_angle = 50
    max_angle = 130

    print("min")
    set_angle_slow(90, min_angle)
    sleep(1)
    print("max")
    set_angle_slow(min_angle, max_angle)
    sleep(1)
    print("mid")
    set_angle_slow(max_angle, 90)
    sleep(1)

    head_angle_current = 90

    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (1280, 720)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()

    while(True):
        try:
            frame = picam2.capture_array()
            height, width, _ = frame.shape
            #print(f"frame h/w = {height}/{width}")

            results = model.predict(frame, conf=0.25, max_det=1, verbose=False)

            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    class_name = CLASS_NAMES[cls_id]
                    if class_name in ["person", "cat"]:
                        print(f"{class_name} detected!")
                        x,y,w,h = box.xywh[0]
                        x_mapped = ((x/1280)*130)+30
                    
                        head_angle = int(max_angle - ((x/width) * (max_angle-min_angle)))
                        #head_angle = int(remap(x_mapped, IN_MIN,IN_MAX,OUT_MIN,OUT_MAX))
                        #head_angle_ave = head_angle * head_angle_alpha + head_angle_ave * (1.0 - head_angle_alpha)
                        print('cur: ' + str(head_angle_current) + ', new: ' + str(head_angle))
                        servo.angle=head_angle 
                        angle_diff = head_angle - head_angle_current
                        for inc in range(0, abs(angle_diff)):
                            if angle_diff > 0:
                                servo.angle = head_angle_current+inc+1
                            if angle_diff < 0:
                                servo.angle = head_angle_current-inc-1
                            sleep(0.02)

                        head_angle_current = head_angle
        
        except KeyboardInterrupt:
            break

    picam2.stop_recording()

# map one range to another
def remap(x, in_min, in_max, out_min, out_max):

    x_diff = x - in_min

    out_range = out_max - out_min

    in_range = in_max - in_min
    temp_out = x_diff * out_range/in_range + out_min
    #print('x: ' + str(x) + ', temp_out: ' + str(temp_out))
    if out_max < out_min:
        temp = out_max
        out_max = out_min
        out_min = temp

    if temp_out > out_max:
        return out_max
    elif temp_out < out_min:
        return out_min
    else:
        return temp_out


if __name__ == "__main__":
    main()
