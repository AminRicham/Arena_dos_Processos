import shared_struct as ss
from random import randint
from multiprocessing import Array

def iniciaGrid(grid):
    for i in range(len(grid)):
        grid[i] = "-"

def printGrid(grid):
    for i in range (len(grid)):
        print(grid[i], end = " ")
        if ((i+1) % 40) == 0:
            print()

def adicionaBaterias(grid):
    for _ in range (ss.QTD_BATERIAS):
        posicao = randint(0, 799)
        grid[posicao] = "\U000026A1"

def adicionaBarreiras(grid):
    qtdBarreiras = randint(0,15)
#    print(qtdBarreiras)
    for _ in range (qtdBarreiras):
        posicao = randint(0, 799)
        grid[posicao] = "#"

def adicionaElementos(grid):
    adicionaBarreiras(grid)
    adicionaBaterias(grid)

def escreveNoArq(arq, qtdBaterias):
    with open(arq, "a") as arquivo:
        arquivo.write(f"QTD_BATERIAS = {qtdBaterias}")
