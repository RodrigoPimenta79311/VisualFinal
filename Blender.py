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
                except Exception:
                    pass

def processar_comando(comando):
    global selected_function, selected_axis

    try:
        if "|" in comando:
            acao, valor = comando.split("|", 1)
        else:
            acao = comando
            valor = ""

        if acao == "SelectAxis":
            if valor in ["X", "Y", "Z", "Todos"]:
                selected_axis = valor

        elif acao == "ActivateFunction":
            selected_function = valor

        elif acao == "DeactivateFunction":
            selected_function = "None"

        elif acao == "Scale":
            if valor == "Up":
                alterar_tamanho_objeto(ACTIVE_OBJECT_NAME, fator=1.1)
            elif valor == "Down":
                alterar_tamanho_objeto(ACTIVE_OBJECT_NAME, fator=0.9)

        elif acao == "Rotate":
            if valor == "R":
                alterar_rotacao_objeto(ACTIVE_OBJECT_NAME, angulo=15)
            elif valor == "C":
                alterar_rotacao_objeto(ACTIVE_OBJECT_NAME, angulo=-15)

        elif acao == "AddObject":
            adicionar_objeto()

        elif acao == "RemoveObject":
            remover_objeto(ACTIVE_OBJECT_NAME)

    except Exception:
        pass

def adicionar_objeto():
    global ACTIVE_OBJECT_NAME
    bpy.ops.mesh.primitive_cube_add()
    novo_objeto = bpy.context.object
    ACTIVE_OBJECT_NAME = novo_objeto.name

def remover_objeto(obj_name):
    if obj_name in bpy.data.objects:
        objeto = bpy.data.objects[obj_name]
        bpy.data.objects.remove(objeto)

def alterar_tamanho_objeto(obj_name, fator):
    if obj_name in bpy.data.objects:
        objeto = bpy.data.objects[obj_name]
        objeto.scale *= fator

def alterar_rotacao_objeto(obj_name, angulo):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        return

    if selected_axis == "Todos":
        for idx in range(3):
            obj.rotation_euler[idx] += math.radians(angulo)
    else:
        idx = {"X": 0, "Y": 1, "Z": 2}.get(selected_axis, None)
        if idx is not None:
            obj.rotation_euler[idx] += math.radians(angulo)

if __name__ == "__main__":
    thread_servidor = threading.Thread(target=servidor_socket, daemon=True)
    thread_servidor.start()
