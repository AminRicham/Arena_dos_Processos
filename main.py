from multiprocessing import Lock, Array, Process
from robots import processo_robo
import shared_struct as ss
from shared_struct import RoboShared
import gridFunctions
import flagsFunctions

def main():
    grid = Array(typecode_or_type='u', size_or_initializer=ss.GRID_SIZE, lock=True)
    grid_mutex = Lock()

    robots = Array(RoboShared, ss.QTD_ROBOS, lock=True)  # CORRETO
    robots_mutex = Lock()

    flags = Array(typecode_or_type= "i", size_or_initializer=(ss.QTD_FLAGS), lock=True)
    flags_mutex = Lock()

    battery_mutex = [Lock() for _ in range (ss.QTD_BATERIAS)]

    gridFunctions.iniciaGrid(grid)
    gridFunctions.adicionaElementos(grid)
    gridFunctions.printGrid(grid)
    flagsFunctions.initFlags(flags)
    
    
    processos = []
    for i in range(ss.QTD_ROBOS):
        processo = Process(
            target=processo_robo,
            args=(i, grid, flags, robots, robots_mutex, grid_mutex)
        )
        processo.start()
        processos.append(processo)

    for p in processos:
        p.join()


if __name__ == '__main__':
    main()