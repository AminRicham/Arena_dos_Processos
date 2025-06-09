from multiprocessing import Lock, Array
import shared_struct as ss
import grid as gdd

def main():

    grid = Array(typecode_or_type='u', size_or_initializer=ss.GRID_SIZE, lock=True)
    grid_mutex = Lock()

    robots = Array(typecode_or_type='i', size_or_initializer=(5*qtdRobos), lock=True)
    robots_mutex = Lock()

    flags = Array(typecode_or_type= "i", size_or_initializer=qtdFlags, lock=True)
    flags_mutex = Lock()

    battery_mutex = Lock()

    gdd.iniciaGrid(grid)
    gdd.adicionaElementos(grid)
    gdd.printGrid(grid)

if __name__ == '__main__':
    main()