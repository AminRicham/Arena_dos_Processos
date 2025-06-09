from multiprocessing import Lock, Array
import shared_struct as ss
import grid as gdd
def main():
    grid = Array(typecode_or_type='u', size_or_initializer=ss.GRID_SIZE, lock=True)
    #robots = Array(typecode_or_type='i', size_or_initializer=(7*qtdRobos), lock=True)
    #flags = Array(typecode_or_type= "i", size_or_initializer=qtdFlags, lock=True)
    gdd.iniciaGrid(grid)
    gdd.adicionaElementos(grid)
    gdd.printGrid(grid)

if __name__ == '__main__':
    main()