import random
import multiprocessing as mp
import threading
import shared_struct as ss
import gridFunctions
from flagsFunctions import getFlagGameOver
import time
from teclado import ler_tecla
from multiprocessing import shared_memory

grid_mutex = mp.Lock()

class Robot:
    def __init__(self, ID, F, E, V, posicao_x, posicao_y, status, grid, flags, robots_shared, robots_mutex, grid_mutex):
        self.ID = ID
        self.forca = F
        self.energia = E
        self.velocidade = V
        self.posicao_x = posicao_x
        self.posicao_y = posicao_y
        self.status = status  # Vivo ou morto
        self.log = []
        self.grid = grid
        self.flags = flags
        self.robots = robots_shared
        self.robots_mutex = robots_mutex
        self.grid_mutex = grid_mutex

        with self.grid_mutex:
            self.set_grid(self.posicao_x, self.posicao_y, str(self.ID))

    def get_index(self, x, y):
        return y * ss.WIDTH + x

    def get_grid(self, x, y):
        byte_value = self.grid[self.get_index(x, y)]
        return chr(byte_value)

    def set_grid(self, x, y, value):
        index = self.get_index(x, y)
        if isinstance(value, str):
            self.grid[index] = ord(value[0])
        elif isinstance(value, int):
            self.grid[index] = value
        elif isinstance(value, bytes):
            self.grid[index] = value[0]
        else:
            raise ValueError(f"Tipo invÃ¡lido para set_grid: {type(value)}")

    def mover(self):
        if self.energia <= 0 or self.robots[self.ID].status != b"V":
            print(f"RobÃ´ {self.ID} sem energia ou morto.")
            return

        bateria_mais_proxima = None
        menor_distancia = float('inf')
        for y in range(ss.HEIGHT):
            for x in range(ss.WIDTH):
                if self.get_grid(x, y) == "B":
                    distancia = abs(self.posicao_x - x) + abs(self.posicao_y - y)
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        bateria_mais_proxima = (x, y)

        if self.energia < 50:
            self.log.append(f"Robo {self.ID} esta com energia baixa ({self.energia}). Buscando bateria mais proxima.")
            if bateria_mais_proxima:
                bateria_x, bateria_y = bateria_mais_proxima
                dx = 0
                dy = 0
                if self.posicao_x < bateria_x:
                    dx = 1
                elif self.posicao_x > bateria_x:
                    dx = -1
                if dx == 0:
                    if self.posicao_y < bateria_y:
                        dy = 1
                    elif self.posicao_y > bateria_y:
                        dy = -1
            else:
                dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
        else:
            dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])

        nova_posicao_x = max(0, min(ss.WIDTH - 1, self.posicao_x + dx))
        nova_posicao_y = max(0, min(ss.HEIGHT - 1, self.posicao_y + dy))

        with self.grid_mutex:
            destino = self.get_grid(nova_posicao_x, nova_posicao_y)
            if destino == "-":
                self.set_grid(self.posicao_x, self.posicao_y, "-")
                self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y
                self.set_grid(self.posicao_x, self.posicao_y, str(self.ID))
                self.energia -= 1
                self.log.append(f"Robo {self.ID} se moveu para ({self.posicao_x}, {self.posicao_y}). Energia restante: {self.energia}.")
            elif destino == "B":
                self.set_grid(self.posicao_x, self.posicao_y, "-")
                self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y
                self.set_grid(self.posicao_x, self.posicao_y, str(self.ID))
                self.energia = min(100, self.energia + 20)
                self.log.append(f"Robo {self.ID} encontrou uma bateria e recarregou. Energia atual: {self.energia}.")
            elif destino == "#":
                self.log.append(f"Robo {self.ID} encontrou uma barreira em ({nova_posicao_x}, {nova_posicao_y}) e nÃ£o pÃ´de se mover.")
            elif destino.isdigit() and destino != str(self.ID):
                self.duelar(int(destino))

    def duelar(self, outro_robo_id):
        outro_robo = self.robots[outro_robo_id]

        if self.robots[self.ID].status != b"V" or outro_robo.status != b"V":
            return

        if self.forca > outro_robo.forca:
            self.log.append(f"Robo {self.ID} venceu o duelo contra Robo {outro_robo_id}.")
            with self.robots_mutex:
                outro_robo.status = b"M"
            with self.grid_mutex:
                self.set_grid(outro_robo.posicao_x, outro_robo.posicao_y, "-")
        elif self.forca < outro_robo.forca:
            self.log.append(f"Robo {self.ID} perdeu o duelo contra Robo {outro_robo_id}.")
            with self.robots_mutex:
                self.robots[self.ID].status = b"M"
            with self.grid_mutex:
                self.set_grid(self.posicao_x, self.posicao_y, "-")
        else:
            self.log.append(f"Robo {self.ID} e Robo {outro_robo_id} empataram no duelo.")
            with self.robots_mutex:
                outro_robo.status = b"M"
                self.robots[self.ID].status = b"M"
            with self.grid_mutex:
                self.set_grid(self.posicao_x, self.posicao_y, "-")
                self.set_grid(outro_robo.posicao_x, outro_robo.posicao_y, "-")
