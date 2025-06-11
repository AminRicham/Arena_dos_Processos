import ctypes

WIDTH = 40
HEIGHT = 20
GRID_SIZE = WIDTH * HEIGHT
TOTAL_SIZE = GRID_SIZE + 4  # 4 bytes para o inteiro game_over
QTD_ROBOS = 1
QTD_FLAGS = 3
QTD_BATERIAS = 15

class RoboShared(ctypes.Structure):
    _fields_ = [
        ("ID", ctypes.c_int),
        ("forca", ctypes.c_int),
        ("energia", ctypes.c_int),
        ("velocidade", ctypes.c_int),
        ("posicao_x", ctypes.c_int),
        ("posicao_y", ctypes.c_int),
        ("status", ctypes.c_char),  # 'V', 'M'
    ]