import shared_struct as ss
from random import randint
from multiprocessing import Array, shared_memory
from array import array
def iniciaGrid(shm_buff):
    """
    Preenche o grid com '-'.
    Args:
        grid: array compartilhado do grid.
    """
    for i in range(ss.GRID_SIZE):
        shm_buff[i] = ord('-')

def printGrid(shm_buff):
    """
    Printa o grid, a cada tamanho de linha printado,
    printa vazio para o proximo print ficar em baixo, visualmente
    Args:
        grid: array compartilhado do grid.
    """
    for i in range (ss.GRID_SIZE):
        print(chr(shm_buff[i]), end = " ")
        if ((i+1) % ss.WIDTH) == 0:
            print()

def adicionaBaterias(shm_buff):
    """
    Adiciona as baterias, com um numero pré definido, ao grid de maneira aleatória
    Args:
        grid: array compartilhado do grid.
    """
    for _ in range (ss.QTD_BATERIAS):
        posicao = randint(0, 799)
        shm_buff[posicao] = ord('B')

def adicionaBarreiras(shm_buff):
    """
    Adiciona as barreiras, com um numero aleatório, ao grid de maneira aleatória
    Args:
        grid: array compartilhado do grid.
    """
    qtdBarreiras = randint(0,15)
#    print(qtdBarreiras)
    for _ in range (qtdBarreiras):
        posicao = randint(0, 799)
        shm_buff[posicao] = ord("#")

def adicionaElementos(shm_buff):
    """
    Adiciona as baterias e barreiras ao grid
    Args:
        grid: array compartilhado do grid.
    """
    adicionaBarreiras(shm_buff)
    adicionaBaterias(shm_buff)

try:
    shm = shared_memory.SharedMemory(name = "arena_dos_robos", create=True, size=ss.TOTAL_SIZE)
#       grid = Array(typecode_or_type='u', size_or_initializer=ss.GRID_SIZE, lock=True)
    iniciaGrid(shm.buf)
    adicionaElementos(shm.buf)
    printGrid(shm.buf)
    shm.close()
    shm.unlink()
except FileExistsError:
    print("Erro na criação da memoria.")



# def escreve_grid_na_shm(shm_buf, grid):
#     for i in range(ss.GRID_SIZE):
#         shm_buf[i] = ord(grid[i]) 
        
# def atualiza_grid_na_shm(shm_buf, grid):
#     for i in range(ss.GRID_SIZE):
#         shm_buf[i] = ord(grid[i]) if isinstance(grid[i], str) else ord(chr(grid[i]))


# def iniciaGrid(grid):
#     """
#     Preenche o grid com '-'.
#     Args:
#         grid: array compartilhado do grid.
#     """
#     for i in range(len(grid)):
#         grid[i] = "-"

# def printGrid(grid):
#     """
#     Printa o grid, a cada tamanho de linha printado,
#     printa vazio para o proximo print ficar em baixo, visualmente
#     Args:
#         grid: array compartilhado do grid.
#     """
#     for i in range (len(grid)):
#         print(grid[i], end = " ")
#         if ((i+1) % ss.WIDTH) == 0:
#             print()

# def adicionaBaterias(grid):
#     """
#     Adiciona as baterias, com um numero pré definido, ao grid de maneira aleatória
#     Args:
#         grid: array compartilhado do grid.
#     """
#     for _ in range (ss.QTD_BATERIAS):
#         posicao = randint(0, 799)
#         grid[posicao] = "B"

# def adicionaBarreiras(grid):
#     """
#     Adiciona as barreiras, com um numero aleatório, ao grid de maneira aleatória
#     Args:
#         grid: array compartilhado do grid.
#     """
#     qtdBarreiras = randint(0,15)
# #    print(qtdBarreiras)
#     for _ in range (qtdBarreiras):
#         posicao = randint(0, 799)
#         grid[posicao] = "#"

# def adicionaElementos(grid):
#     """
#     Adiciona as baterias e barreiras ao grid
#     Args:
#         grid: array compartilhado do grid.
#     """
#     adicionaBarreiras(grid)
#     adicionaBaterias(grid)