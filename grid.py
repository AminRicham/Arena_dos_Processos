import random
from robots import Robot

class Grid:
    def __init__(self, x: int,y: int,): #robos: Robot
        self.x = x
        self.y = y
        self.qtd_itemEnergia = random.randint(3, 10)
        self.qtd_itemBarreira = random.randint(3, 10)
        self.posicoesTomadas = []
        self.grid = self.createGridBase()
        self.adicionaElementos()

    def createGridBase(self):
        grid = []
        for _ in range(self.x):
            row = []
            for _ in range(self.y):
                row.append('-')
            grid.append(row)
        return grid

    def adicionaElementos(self):
        self.adicionaBarreiras()
        self.adicionaBaterias()

    def adicionaBaterias(self):
        for _ in range (self.qtd_itemEnergia - 1):
            posicaoX = random.randint(0, self.x - 1)
            posicaoY = random.randint(0, self.y - 1)
            if (posicaoX, posicaoY) not in self.posicoesTomadas:
                self.grid[posicaoX][posicaoY] = "\U000026A1"
                self.posicoesTomadas.append((posicaoX, posicaoY))

    def adicionaBarreiras(self):
        try:
            for _ in range (self.qtd_itemBarreira - 1):
                posicaoX = random.randint(0, self.x - 1)
                posicaoY = random.randint(0, self.y - 1)
                if  (posicaoX, posicaoY) not in self.posicoesTomadas:
                    self.grid[posicaoX][posicaoY] = "#"
                    self.posicoesTomadas.append((posicaoX, posicaoY))
        except Exception as e:
            print(e)

    def printGrid(self):
        for row in self.grid:
            print(" ".join(row))