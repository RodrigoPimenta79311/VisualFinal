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

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"O modelo não foi encontrado. Verifique o caminho: {MODEL_PATH}")

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
    "pen": "Adicionar",
    "cup": "Remover",
    "bowl": "Escalar",
    "toothbrush": "Rotate"
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

def detectar_objetos(detector, frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    return detector.detect(mp_image)

def enviar_comando_para_blender(comando):
    global ultimo_comando_enviado
    tempo_atual = time.time()

    if tempo_atual - ultimo_comando_enviado < DELAY_COMANDOS:
        return

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(comando.encode('utf-8'))
        ultimo_comando_enviado = tempo_atual
    except ConnectionRefusedError:
        pass

def detectar_movimento_cabeca(landmarks, image_width):
    global indice_atual, eixos, ultimo_movimento_array
    tempo_atual = time.time()

    if tempo_atual - ultimo_movimento_array < DELAY_COMANDOS:
        return None

    nariz = landmarks[1]
    bochecha_esquerda = landmarks[127]
    bochecha_direita = landmarks[356]

    pos_nariz_x = nariz.x * image_width
    pos_bochecha_esquerda_x = bochecha_esquerda.x * image_width
    pos_bochecha_direita_x = bochecha_direita.x * image_width

    if pos_nariz_x > pos_bochecha_direita_x - 10:
        indice_atual = (indice_atual - 1) % len(eixos)
        ultimo_movimento_array = tempo_atual
        return f"SelectAxis|{eixos[indice_atual]}"

    elif pos_nariz_x < pos_bochecha_esquerda_x + 10:
        indice_atual = (indice_atual + 1) % len(eixos)
        ultimo_movimento_array = tempo_atual
        return f"SelectAxis|{eixos[indice_atual]}"

    return None

def detectar_mao_aberta(hand_landmarks, image_height):
    dedos = [(4, 3), (8, 6), (12, 10), (16, 14), (20, 18)]
    dedos_levantados = sum(
        hand_landmarks.landmark[tip_idx].y * image_height <
        hand_landmarks.landmark[pip_idx].y * image_height
        for tip_idx, pip_idx in dedos
    )
    return dedos_levantados >= 4

def detectar_mao_fechada(hand_landmarks, image_height):
    dedos = [(4, 3), (8, 6), (12, 10), (16, 14), (20, 18)]
    dedos_levantados = sum(
        hand_landmarks.landmark[tip_idx].y * image_height <
        hand_landmarks.landmark[pip_idx].y * image_height
        for tip_idx, pip_idx in dedos
    )
    return dedos_levantados <= 1

def controlar_funcao_com_mao_esquerda(hand_landmarks, image_height):
    global funcao_ativa

    if funcao_ativa == "None":
        return

    mao_aberta = detectar_mao_aberta(hand_landmarks, image_height)
    mao_fechada = detectar_mao_fechada(hand_landmarks, image_height)

    if funcao_ativa == "Rotate":
        if mao_aberta:
            enviar_comando_para_blender("Rotate|R")
        elif mao_fechada:   
            enviar_comando_para_blender("Rotate|C")
    elif funcao_ativa == "Adicionar":
        if mao_aberta:
            enviar_comando_para_blender("AddObject")

    elif funcao_ativa == "Remover":
        if mao_fechada:
            enviar_comando_para_blender("RemoveObject")

    elif funcao_ativa == "Escalar":
        if mao_aberta:
            enviar_comando_para_blender("Scale|Up")
        elif mao_fechada:
            enviar_comando_para_blender("Scale|Down")

def mostrar_estado(frame):
    global eixos, indice_atual, funcao_ativa
    texto_eixo = f"Eixo Atual: {eixos[indice_atual]}"
    texto_funcao = f"Função Ativa: {funcao_ativa}"

    cv2.putText(frame, texto_eixo, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, texto_funcao, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

def main():
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    object_detector_options = vision.ObjectDetectorOptions(
        base_options=base_options, 
        score_threshold=0.2
    )
    detector_objetos = vision.ObjectDetector.create_from_options(object_detector_options)

    cap = cv2.VideoCapture(0)

    hands_solution = mp_hands.Hands(
        max_num_hands=2, 
        min_detection_confidence=0.7, 
        min_tracking_confidence=0.5
    )
    face_mesh_solution = mp_face_mesh.FaceMesh(
        refine_landmarks=True, 
        min_detection_confidence=0.7, 
        min_tracking_confidence=0.5
    )

    global funcao_ativa

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_height, image_width, _ = frame.shape

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        detection_result = detector_objetos.detect(mp_image)
        objeto_detectado = visualizar_objetos(frame, detection_result)

        if objeto_detectado:
            objeto_detectado_normalizado = objeto_detectado.lower()
            if objeto_detectado_normalizado in objetos_para_funcoes:
                nova_funcao = objetos_para_funcoes[objeto_detectado_normalizado]
                if funcao_ativa != nova_funcao:
                    funcao_ativa = nova_funcao
                    enviar_comando_para_blender(f"ActivateFunction|{funcao_ativa}")

        results_hands = hands_solution.process(frame_rgb)
        if results_hands.multi_hand_landmarks and results_hands.multi_handedness:
            for hand_landmarks, handedness in zip(
                results_hands.multi_hand_landmarks,
                results_hands.multi_handedness
            ):
                label = handedness.classification[0].label

                if label == 'Left':
                    controlar_funcao_com_mao_esquerda(hand_landmarks, image_height)

                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

        results_face = face_mesh_solution.process(frame_rgb)
        if results_face.multi_face_landmarks:
            for face_landmarks in results_face.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS
                )
                comando_cabeca = detectar_movimento_cabeca(face_landmarks.landmark, image_width)
                if comando_cabeca:
                    enviar_comando_para_blender(comando_cabeca)

        mostrar_estado(frame)

        cv2.imshow("Demo", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
