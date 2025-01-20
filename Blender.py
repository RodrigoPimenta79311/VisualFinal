import bpy
import socket
import threading
import math

HOST = "127.0.0.1"
PORT = 65432

ACTIVE_OBJECT_NAME = "Cube"
selected_function = "None"
selected_axis = "Todos"
