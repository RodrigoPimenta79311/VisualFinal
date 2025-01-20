import bpy
import socket
import threading
import math

HOST = "127.0.0.1"
PORT = 65432

ACTIVE_OBJECT_NAME = bpy.context.selected_objects #"Cube"

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
                        print(f"[Blender] Comando recebido: {comando}")
                        processar_comando(comando)
                except Exception as e:
                    print(f"[Blender] Erro ao processar comando: {e}")

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
            if valor == "Clockwise":
                rotacionar_objeto(ACTIVE_OBJECT_NAME, sentido=1)
            elif valor == "CounterClockwise":
                rotacionar_objeto(ACTIVE_OBJECT_NAME, sentido=-1)

        elif acao == "AddObject":
            adicionar_objeto()

        elif acao == "RemoveObject":
            remover_objeto(ACTIVE_OBJECT_NAME)

    except Exception as e:
        print(f"[Blender] Erro ao processar o comando '{comando}': {e}")

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
        ACTIVE_OBJECT_NAME = ""  # Não há objeto ativo agora
    

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

def rotacionar_objeto(obj_name, sentido):

    obj = bpy.data.objects.get(obj_name)
    if not obj:
      
        return
    graus_por_passo = 15
    valor_rotacao = math.radians(graus_por_passo) * sentido

    if selected_axis == "Todos":
        obj.rotation_euler = [
            angle + valor_rotacao for angle in obj.rotation_euler
        ]
    else:
        idx = {"X": 0, "Y": 1, "Z": 2}.get(selected_axis, None)
        if idx is not None:
            obj.rotation_euler[idx] += valor_rotacao

    print(f"[Blender] Objeto '{obj_name}' rotacionado em {selected_axis} (valor={math.degrees(valor_rotacao)}°).")

if __name__ == "__main__":
    thread_servidor = threading.Thread(target=servidor_socket, daemon=True)
    thread_servidor.start()
    print("[Blender] Servidor iniciado.")