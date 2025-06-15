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
        # Garante que memória com o mesmo nome não exista antes de criar
        try:
            existing_shm = shared_memory.SharedMemory(name=shm_name)
            existing_shm.close()
            existing_shm.unlink()
        except FileNotFoundError:
            pass 

        shm = shared_memory.SharedMemory(name=shm_name, create=True, size=ss.TOTAL_SIZE + 4)
    except FileExistsError as e:
        print(f"Erro na criação da memoria: {e}")
        return

    manager = Manager()

    grid_mutex = manager.Lock()
    robots_mutex = manager.Lock()
    flags_mutex = manager.Lock()

    robots = Array(RoboShared, ss.QTD_ROBOS, lock=True)
    flags = Array(typecode_or_type= "i", size_or_initializer=(ss.QTD_FLAGS), lock=True)

    gridFunctions.iniciaGrid(shm.buf)
    gridFunctions.adicionaElementos(shm.buf)
    gridFunctions.printGrid(shm.buf)

    flagsFunctions.initFlags(flags, shm.buf)

    processos = []
    for i in range(ss.QTD_ROBOS):
        # O robô de ID 0 é o jogador
        if i == 0:
            processo = Process(
                target=processo_jogador,
                args=(i, flags, robots, robots_mutex, grid_mutex, flags_mutex, shm_name)
            )
        else:
            processo = Process(
                target=processo_robo,
                args=(i, flags, robots, robots_mutex, grid_mutex, flags_mutex, shm_name)
            )
        processo.start()
        processos.append(processo)

    # Espera todos os processos terminarem
    for p in processos:
        p.join()
    
    shm.close()
    shm.unlink()

if __name__ == '__main__':
    main()
