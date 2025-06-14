import time
from multiprocessing import shared_memory
from shared_struct import WIDTH, HEIGHT, GRID_SIZE, TOTAL_SIZE

def main():
    try:
        shm = shared_memory.SharedMemory(name="arena_dos_robos", create=True, size=TOTAL_SIZE)
    except FileExistsError:
        shm = shared_memory.SharedMemory(name="arena_dos_robos", create=False, size=TOTAL_SIZE)

    grid = bytearray(b' ' * GRID_SIZE)
    grid[2*WIDTH + 3] = ord('#')
    grid[4*WIDTH + 6] = ord('B')
    grid[10*WIDTH + 15] = ord('1')
    grid[11*WIDTH + 15] = ord('2')

    shm.buf[:GRID_SIZE] = grid
    shm.buf[GRID_SIZE:GRID_SIZE+4] = (0).to_bytes(4, "little")

    print("Simulador rodando por 5 segundos...")
    time.sleep(5)
    shm.buf[GRID_SIZE:GRID_SIZE+4] = (1).to_bytes(4, "little")
    print("Fim de jogo sinalizado.")

    time.sleep(1)
    shm.close()
    shm.unlink()

if __name__ == "__main__":
    main()