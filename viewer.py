import time
import os
from multiprocessing import shared_memory
from shared_struct import WIDTH, HEIGHT, GRID_SIZE, TOTAL_SIZE
import ctypes

NUM_ROBOS = 10  # Ajuste conforme o total de robôs usados

class RobotStruct(ctypes.Structure):
    _fields_ = [
        ('ID', ctypes.c_int),
        ('forca', ctypes.c_int),
        ('energia', ctypes.c_int),
        ('velocidade', ctypes.c_int),
        ('posicao_x', ctypes.c_int),
        ('posicao_y', ctypes.c_int),
        ('status', ctypes.c_char)
    ]
#Atualizar o Grid
def render(grid_bytes):
    os.system("cls" if os.name == "nt" else "clear")
    print("=== ARENA DOS ROBÔS ===")
    for i in range(HEIGHT):
        linha = grid_bytes[i*WIDTH:(i+1)*WIDTH].decode('utf-8')
        print(linha)
    print()
#percorre cara linha buscando os robos 
def contar_robos_vivos(robots_buf):
    vivos = 0
    vencedor_id = -1
    for i in range(NUM_ROBOS):
        offset = i * ctypes.sizeof(RobotStruct)
        robot = RobotStruct.from_buffer_copy(robots_buf[offset:offset + ctypes.sizeof(RobotStruct)])
        if robot.status == b"V":
            vivos += 1
            vencedor_id = robot.ID
    return vivos, vencedor_id

def main():
    try:
        shm = shared_memory.SharedMemory(name="arena_dos_robos")
    except FileNotFoundError:
        print("Memória compartilhada não encontrada.")
        return

    while True:
        buffer = shm.buf[:TOTAL_SIZE]
        grid_bytes = bytes(buffer[:GRID_SIZE])
        game_over_flag = int.from_bytes(buffer[GRID_SIZE:GRID_SIZE+4], "little")
        robots_buf = buffer[GRID_SIZE+4:]

        render(grid_bytes)

        vivos, vencedor_id = contar_robos_vivos(robots_buf)
        if vivos == 1:
            print(f"\n\n🏆 FIM DE JOGO! ROBO {vencedor_id} VENCEU!!! 🏆\n")
            break
        elif vivos == 0:
            print("\n\n💀 FIM DE JOGO! TODOS OS ROBÔS FORAM DESTRUIDOS. EMPATE! 💀\n")
            break

        if game_over_flag == 1:
            print("Fim de jogo detectado pela flag.")
            break

        time.sleep(0.2)

    del grid_bytes
    del buffer
    shm.close()

if __name__ == "__main__":
    main()
