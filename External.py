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

DELAY_COMANDOS = 0.5
ultimo_comando_enviado = 0
ultimo_movimento_array = 0

eixos = ["Todos", "X", "Y", "Z"]
indice_atual = 0
funcao_ativa = "None"

objetos_para_funcoes = {
    "hammer": "Adicionar",
    "toothbrush": "Remover",
    "bowl": "Escalar",
    "ball": "Rotate",
    "corno": "Selecionar"
}

objetos_para_ignorar = ["person", "cat", "dog"]

def inicializar_detector_objetos():
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    object_detector_options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.5)
    return vision.ObjectDetector.create_from_options(object_detector_options)

def visualizar_objetos(image, detection_result):
    detected_object = None
    for detection in detection_result.detections:
        bbox = detection.bounding_box
        category = detection.categories[0]
        category_name = category.category_name.lower()

        if category_name in objetos_para_ignorar:
            continue

        start_point = (int(bbox.origin_x), int(bbox.origin_y))
        end_point = (int(bbox.origin_x + bbox.width), int(bbox.origin_y + bbox.height))
        cv2.rectangle(image, start_point, end_point, (255, 0, 0), 3)

        probability = round(category.score, 2)
        result_text = f"{category_name} ({probability})"
        text_location = (int(bbox.origin_x), int(bbox.origin_y) - 10)
        cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        if detected_object is None:
            detected_object = category_name

    return detected_object
