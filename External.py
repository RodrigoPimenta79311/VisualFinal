import cv2
import mediapipe as mp
import socket
import time
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILENAME = "efficientdet_lite0.tflite"
MODEL_PATH = "C:/Users/admin/Desktop/Visu/efficientdet_lite0.tflite"

if os.path.exists(MODEL_PATH):
    pass
else:
    pass

HOST = "127.0.0.1"
PORT = 65432

mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
