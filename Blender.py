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

        elif acao == "Selecionar":
            atualizar_objeto_ativo(comando)

    except Exception:
        pass

def adicionar_objeto():
    global ACTIVE_OBJECT_NAME
    bpy.ops.mesh.primitive_cube_add()
    new_obj = bpy.context.active_object
    ACTIVE_OBJECT_NAME = new_obj.name

def remover_objeto(obj_name):
    global ACTIVE_OBJECT_NAME
    obj = bpy.data.objects.get(obj_name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)
        ACTIVE_OBJECT_NAME = ""

def alterar_tamanho_objeto(obj_name, fator):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        return

    if selected_axis == "Todos":
        obj.scale *= fator
    else:
        idx = {"X": 0, "Y": 1, "Z": 2}.get(selected_axis, None)
        if idx is not None:
            obj.scale[idx] *= fator

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

def listar_objetos_na_cena():
    return [obj.name for obj in bpy.data.objects]

def atualizar_objeto_ativo(comando):
    global ACTIVE_OBJECT_NAME
    objetos = listar_objetos_na_cena()

    if not objetos:
        return

    if ACTIVE_OBJECT_NAME not in objetos:
        ACTIVE_OBJECT_NAME = objetos[0]

    idx_atual = objetos.index(ACTIVE_OBJECT_NAME)

    if comando == "Selecionar|Up":
        idx_proximo = (idx_atual + 1) % len(objetos)
    elif comando == "Selecionar|Down":
        idx_proximo = (idx_atual - 1) % len(objetos)
    else:
        return

    ACTIVE_OBJECT_NAME = objetos[idx_proximo]
    bpy.context.view_layer.objects.active = bpy.data.objects[ACTIVE_OBJECT_NAME]

if __name__ == "__main__":
    thread_servidor = threading.Thread(target=servidor_socket, daemon=True)
    thread_servidor.start()

ACTIVE_OBJECT_NAME = "Cube"
selected_function = "None"
selected_axis = "Todos"

try:
    # Operações principais
except Exception as e:
    pass