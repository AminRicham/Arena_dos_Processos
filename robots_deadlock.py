import random
import multiprocessing as mp
import threading
import shared_struct as ss
import gridFunctions
from flagsFunctions import getFlagGameOver, setFlagGameOver, setFlagVencedor
import time
from teclado import ler_tecla
from multiprocessing import shared_memory
import os

class Robot:
    def __init__(self, ID, F, E, V, posicao_x, posicao_y, status, grid, flags, robots_shared, robots_mutex, grid_mutex, flags_mutex):
        self.ID = ID
        self.forca = F
        self.energia = E
        self.velocidade = V
        self.posicao_x = posicao_x
        self.posicao_y = posicao_y
        self.status = status
        self.log = []
        self.grid = grid
        self.flags = flags
        self.robots = robots_shared
        self.robots_mutex = robots_mutex
        self.grid_mutex = grid_mutex
        self.flags_mutex = flags_mutex


        with self.robots_mutex:
            self.robots[self.ID].ID = self.ID
            self.robots[self.ID].forca = self.forca
            self.robots[self.ID].energia = self.energia
            self.robots[self.ID].velocidade = self.velocidade
            self.robots[self.ID].posicao_x = self.posicao_x
            self.robots[self.ID].posicao_y = self.posicao_y
            self.robots[self.ID].status = self.status

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
        else:
            self.grid[index] = value

    def _check_game_over(self):
        with self.flags_mutex:
            if getFlagGameOver(self.flags) == 1:
                return

            vivos = 0
            vencedor_id = -1
            with self.robots_mutex:
                for i in range(ss.QTD_ROBOS):
                    if self.robots[i].status == b'V':
                        vivos += 1
                        vencedor_id = self.robots[i].ID
            
            if vivos <= 1:
                setFlagVencedor(self.flags, vencedor_id)
                setFlagGameOver(self.flags, 1, self.grid)
                if vencedor_id != -1:
                    print(f"\nO Robô {vencedor_id} é o vencedor!")
                else:
                    print("\nTodos os robôs foram destruídos. Empate!")


    def mover(self):
        
        bateria_mais_proxima = None
        menor_distancia = float('inf')
        for y in range(ss.HEIGHT):
            for x in range(ss.WIDTH):
                if self.get_grid(x, y) == "B":
                    distancia = abs(self.posicao_x - x) + abs(self.posicao_y - y)
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        bateria_mais_proxima = (x, y)
        
        dx, dy = 0, 0
        if self.energia < 50 and bateria_mais_proxima:
            self.log.append(f"Robo {self.ID} com energia baixa ({self.energia}). Buscando bateria.")
            bateria_x, bateria_y = bateria_mais_proxima
            if self.posicao_x < bateria_x: dx = 1
            elif self.posicao_x > bateria_x: dx = -1
            elif self.posicao_y < bateria_y: dy = 1
            elif self.posicao_y > bateria_y: dy = -1
        else:
            dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])

        self.mover_para(dx, dy)

    def mover_para(self, dx, dy):
        if self.status != b'V':
            return
            
        nova_posicao_x = max(0, min(ss.WIDTH - 1, self.posicao_x + dx))
        nova_posicao_y = max(0, min(ss.HEIGHT - 1, self.posicao_y + dy))
        
        with self.grid_mutex:
            destino = self.get_grid(nova_posicao_x, nova_posicao_y)
            if destino == "-":
                self.set_grid(self.posicao_x, self.posicao_y, "-")
                self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y
                self.set_grid(self.posicao_x, self.posicao_y, str(self.ID))
                self.energia -= 1
            elif destino == "B":
                self.set_grid(self.posicao_x, self.posicao_y, "-")
                self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y
                self.set_grid(self.posicao_x, self.posicao_y, str(self.ID))
                self.energia = min(100, self.energia + 20)
            elif destino == "#":
                pass
            elif destino.isdigit() and destino != str(self.ID):
                self.duelar(int(destino), nova_posicao_x, nova_posicao_y)
        
        if self.ID == 0: # Limpa a tela e mostra o grid para o jogador
            os.system("cls" if os.name == "nt" else "clear")
            print(f"Jogador {self.ID} | Energia: {self.energia} | Força: {self.forca}")
            gridFunctions.printGrid(self.grid)


    def duelar(self, outro_robo_id, x_duelo, y_duelo):
        with self.robots_mutex:
            outro_robo_forca = self.robots[outro_robo_id].forca
            outro_robo_status = self.robots[outro_robo_id].status

            if self.status != b"V" or outro_robo_status != b"V":
                return

            print(f"\nDUELO: Robô {self.ID} (F:{self.forca}) vs Robô {outro_robo_id} (F:{outro_robo_forca})")
            
            if self.forca > outro_robo_forca:
                print(f"Robô {self.ID} venceu!")
                self.log.append(f"Venceu duelo contra {outro_robo_id}.")
                self.robots[outro_robo_id].status = b"M"
                with self.grid_mutex:
                    self.set_grid(self.posicao_x, self.posicao_y, "-") 
                    self.set_grid(x_duelo, y_duelo, str(self.ID))
                self.posicao_x, self.posicao_y = x_duelo, y_duelo
            
            elif self.forca < outro_robo_forca:
                print(f"Robô {outro_robo_id} venceu!")
                self.log.append(f"Perdeu duelo para {outro_robo_id}.")
                self.status = b"M" # Atualiza o status local para sair dos loops
                self.robots[self.ID].status = b"M"
                with self.grid_mutex:
                    self.set_grid(self.posicao_x, self.posicao_y, "-")

            else: # Empate
                print("Empate! Ambos foram destruídos.")
                self.log.append(f"Empatou duelo com {outro_robo_id}.")
                self.status = b"M" # Atualiza o status local
                self.robots[self.ID].status = b"M"
                self.robots[outro_robo_id].status = b"M"
                with self.grid_mutex:
                    self.set_grid(self.posicao_x, self.posicao_y, "-")
                    self.set_grid(x_duelo, y_duelo, "-")
        
        time.sleep(0.5) 
        self._check_game_over()

    def sense_act(self):
        while True:
            # CORREÇÃO: Verifica o status na memória compartilhada a cada ciclo
            with self.robots_mutex:
                if self.robots[self.ID].status != b'V':
                    break
            
            if getFlagGameOver(self.flags) == 1:
                break

            self.mover()
            time.sleep(self.velocidade * 0.2)

    def housekeeping(self):
        while True:
            # CORREÇÃO: Verifica o status na memória compartilhada a cada ciclo
            with self.robots_mutex:
                if self.robots[self.ID].status != b'V':
                    break

            if getFlagGameOver(self.flags) == 1:
                break
            
            time.sleep(1)
            self.energia -= 1
            if self.energia <= 0:
                self.status = b"M" # Atualiza status local
                with self.robots_mutex:
                    self.robots[self.ID].status = b"M" # Atualiza status compartilhado
                with self.grid_mutex:
                    self.set_grid(self.posicao_x, self.posicao_y, "-")
                self.log.append(f"Robo {self.ID} ficou sem energia e foi desligado.")
                self._check_game_over()
                break


    def iniciar(self):
        t_sense_act = threading.Thread(target=self.sense_act)
        t_housekeeping = threading.Thread(target=self.housekeeping)
        t_sense_act.start()
        t_housekeeping.start()
        t_sense_act.join()
        t_housekeeping.join()
        
        # CORREÇÃO: Escrita correta do log
        with open(f"robo_{self.ID}_log.txt", "w", encoding="utf-8") as f:
            f.write(f"--- LOG Robô {self.ID} ---\n")
            for linha in self.log:
                f.write(linha + "\n")
            f.write("--- FIM LOG ---\n")


def processo_robo(ID, flags, robots_shared, robots_mutex, grid_mutex, flags_mutex, shm_name):
    shm = shared_memory.SharedMemory(name=shm_name)
    grid = shm.buf
    
    F = random.randint(1, 10)
    E = random.randint(50, 100)
    V = random.randint(1, 5)

    with grid_mutex:
        while True:
            posicao_x = random.randint(0, ss.WIDTH - 1)
            posicao_y = random.randint(0, ss.HEIGHT - 1)
            if chr(grid[posicao_y * ss.WIDTH + posicao_x]) == '-':
                break
    
    robo = Robot(ID, F, E, V, posicao_x, posicao_y, b"V", grid, flags, robots_shared, robots_mutex, grid_mutex, flags_mutex)
    robo.iniciar()
    shm.close()

def processo_jogador(ID, flags, robots_shared, robots_mutex, grid_mutex, flags_mutex, shm_name):
    shm = shared_memory.SharedMemory(name=shm_name)
    grid = shm.buf

    F = 100
    E = 100
    V = 1

    with grid_mutex:
        while True:
            posicao_x = random.randint(0, ss.WIDTH - 1)
            posicao_y = random.randint(0, ss.HEIGHT - 1)
            if chr(grid[posicao_y * ss.WIDTH + posicao_x]) == '-':
                break
    
    robo = Robot(ID, F, E, V, posicao_x, posicao_y, b"V", grid, flags, robots_shared, robots_mutex, grid_mutex, flags_mutex)
    
    controles = {'w': (0, -1), 's': (0, 1), 'a': (-1, 0), 'd': (1, 0)}
    
    t_housekeeping = threading.Thread(target=robo.housekeeping)
    t_housekeeping.start()

    os.system("cls" if os.name == "nt" else "clear")
    print("Controle ativado: use W, A, S, D para se movimentar. Pressione Q para sair.")
    print(f"Jogador {robo.ID} | Energia: {robo.energia} | Força: {robo.forca}")
    gridFunctions.printGrid(robo.grid)

    while True:
        # CORREÇÃO: Verifica o status na memória compartilhada a cada ciclo
        with robots_mutex:
            if robots_shared[robo.ID].status != b'V':
                print("\nVocê foi derrotado!")
                break
        
        if getFlagGameOver(flags) == 1:
            break

        tecla = ler_tecla().lower()
        if tecla in controles:
            dx, dy = controles[tecla]
            robo.mover_para(dx, dy)
        elif tecla == 'q':
            print("Você saiu do jogo.")
            robo.status = b'M' # Marca como morto ao sair
            with robots_mutex:
                robots_shared[robo.ID].status = b'M'
            break
    
    robo._check_game_over()
    t_housekeeping.join()
    shm.close()