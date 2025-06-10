from multiprocessing import Lock, Array
from multiprocessing.sharedctypes import Array as SharedArray
import shared_struct as ss
from shared_struct import RoboShared
import gridFunctions
import flagsFunctions

def main():
    grid = Array(typecode_or_type='u', size_or_initializer=ss.GRID_SIZE, lock=True)
    grid_mutex = Lock()

    robots = SharedArray(RoboShared, ss.QTD_ROBOS)
    robots_mutex = Lock()

    flags = Array(typecode_or_type= "i", size_or_initializer=(ss.QTD_FLAGS), lock=True)
    flags_mutex = Lock()

    battery_mutex = [Lock() for _ in range (ss.QTD_BATERIAS)]

    gridFunctions.iniciaGrid(grid)
    flagsFunctions.initFlags(flags)


if __name__ == '__main__':
    main()