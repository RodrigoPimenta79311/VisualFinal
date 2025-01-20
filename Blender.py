import bpy
import socket
import threading
import math

HOST = "127.0.0.1"
PORT = 65432

ACTIVE_OBJECT_NAME = "Cube"
selected_function = "None"
selected_axis = "Todos"

def servidor_socket():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                try:
                    data = conn.recv(1024)
                    if data:
                        comando = data.decode('utf-8').strip()
                        processar_comando(comando)
                except Exception as e:
                    pass
