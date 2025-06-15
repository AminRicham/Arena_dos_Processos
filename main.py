from multiprocessing import Manager, Array, Process, shared_memory
from robots import processo_robo, processo_jogador
import shared_struct as ss
from shared_struct import RoboShared
import gridFunctions
import flagsFunctions

def main():
    """Criação da memoria compartilhada"""
    shm_name = "arena_dos_robos"
    try:
        shm = shared_memory.SharedMemory(name = shm_name, create=True, size=ss.TOTAL_SIZE + 1)

#       grid = Array(typecode_or_type='u', size_or_initializer=ss.GRID_SIZE, lock=True)
    except FileExistsError as e:
        print("Erro na criação da memoria:", e)
        return

    grid_mutex = Lock()

    robots = Array(RoboShared, ss.QTD_ROBOS, lock=True)  # CORRETO
    robots_mutex = Lock()

    flags = Array(typecode_or_type= "i", size_or_initializer=(ss.QTD_FLAGS), lock=True)
    flags_mutex = Lock()

    battery_mutex = [Lock() for _ in range (ss.QTD_BATERIAS)]

    gridFunctions.iniciaGrid(shm.buf)
    gridFunctions.adicionaElementos(shm.buf)
    gridFunctions.printGrid(shm.buf)

    flagsFunctions.initFlags(flags, shm.buf)

    processos = []
    for i in range(ss.QTD_ROBOS):
        if i == 0:
            processo = Process(
                target=processo_jogador,
                args=(i, flags, robots, robots_mutex, grid_mutex, shm_name)
            )
        else:
            processo = Process(
                target=processo_robo,
                args=(i, flags, robots, robots_mutex, grid_mutex, shm_name)
            )

        processo.start()
        processos.append(processo)

    for p in processos:
        p.join()
    
    shm.close()
    shm.unlink()

if __name__ == '__main__':
    main()
