import time
import os
from multiprocessing import shared_memory
from shared_struct import WIDTH, HEIGHT, GRID_SIZE, TOTAL_SIZE

def render(grid_bytes):
    os.system("cls" if os.name == "nt" else "clear")
    print("=== ARENA DOS ROBÔS ===")
    for i in range(HEIGHT):
        linha = grid_bytes[i*WIDTH:(i+1)*WIDTH].decode('utf-8')
        print(linha)
    print()

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

        render(grid_bytes)

        if game_over_flag == 1:
            print("Fim de jogo detectado.")
            break

        time.sleep(0.2)

    # Libera referências antes de fechar
    del grid_bytes
    del buffer
    shm.close()

if __name__ == "__main__":
    main()
