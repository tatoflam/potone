#!/usr/bin/python 

# coding=UTF-8 
import cv2 
import numpy as np

from constants import KEY_ESC, KEY_SAVE, KEY_RECEIVER_STOP, WINDOW_ORG, WINDOW_DIFF, \
     WINDOW_INVERTDIFF, WINDOW_MOSAIC, PICTURE_DIR, SERIAL_PORT, SERIAL_STOP, \
     LIST_USB_COMMAND

def mosaic(frame, ratio=0.05):
    imageSmall = cv2.resize(frame, None, fx=ratio, fy=ratio,
                            interpolation=cv2.INTER_NEAREST)
    frame = cv2.resize(imageSmall, frame.shape[:2][::-1],
                        interpolation=cv2.INTER_NEAREST)
    return frame

def invert_color(frame):
    # invert color
    frame = cv2.bitwise_not(frame.astype(np.uint8))
    return frame
