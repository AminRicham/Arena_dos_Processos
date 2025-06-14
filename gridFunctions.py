import shared_struct as ss
from random import randint
from multiprocessing import Array


def iniciaGrid(grid):
    """
    Preenche o grid com '-'.
    Args:
        grid: array compartilhado do grid.
    """
    for i in range(len(grid)):
        grid[i] = "-"

def printGrid(grid):
    """
    Printa o grid, a cada tamanho de linha printado,
    printa vazio para o proximo print ficar em baixo, visualmente
    Args:
        grid: array compartilhado do grid.
    """
    for i in range (len(grid)):
        print(grid[i], end = " ")
        if ((i+1) % ss.WIDTH) == 0:
            print()

def adicionaBaterias(grid):
    """
    Adiciona as baterias, com um numero pré definido, ao grid de maneira aleatória
    Args:
        grid: array compartilhado do grid.
    """
    for _ in range (ss.QTD_BATERIAS):
        posicao = randint(0, 799)
        grid[posicao] = "\U000026A1"

def adicionaBarreiras(grid):
    """
    Adiciona as barreiras, com um numero aleatório, ao grid de maneira aleatória
    Args:
        grid: array compartilhado do grid.
    """
    qtdBarreiras = randint(0,15)
#    print(qtdBarreiras)
    for _ in range (qtdBarreiras):
        posicao = randint(0, 799)
        grid[posicao] = "#"

def adicionaElementos(grid):
    """
    Adiciona as baterias e barreiras ao grid
    Args:
        grid: array compartilhado do grid.
    """
    adicionaBarreiras(grid)
    adicionaBaterias(grid)