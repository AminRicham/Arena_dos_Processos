import random
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

        # inicializando o log
        self.log.append(f"Robo {self.ID} iniciado com Força: {self.forca}, Energia: {self.energia}, Velocidade: {self.velocidade}, Posição: ({self.posicao_x}, {self.posicao_y}), Status: {self.status.decode()}")

        # Atualiza o estado do robô na lista compartilhada
        with self.robots_mutex:
            self.robots[self.ID].ID = self.ID
            self.robots[self.ID].forca = self.forca
            self.robots[self.ID].energia = self.energia
            self.robots[self.ID].velocidade = self.velocidade
            self.robots[self.ID].posicao_x = self.posicao_x
            self.robots[self.ID].posicao_y = self.posicao_y
            self.robots[self.ID].status = self.status

        # Atualiza o grid com a posição inicial do robô
        with self.grid_mutex:
            self.set_grid(self.posicao_x, self.posicao_y, str(self.ID))

    def get_index(self, x, y):
        return y * ss.WIDTH + x # Calcula o índice linear para o grid 2D

    def get_grid(self, x, y):
        byte_value = self.grid[self.get_index(x, y)] # Obtém o valor do grid na posição (x, y)
        return chr(byte_value)

    def set_grid(self, x, y, value):
        index = self.get_index(x, y)
        if isinstance(value, str):
            self.grid[index] = ord(value[0])
        else:
            self.grid[index] = value

    # Verifica se o jogo acabou e define o vencedor
    def _check_game_over(self):
        with self.flags_mutex: # Usando mutex das flags
            if getFlagGameOver(self.flags) == 1:
                return

            vivos = 0
            vencedor_id = -1
            with self.robots_mutex:
                # Conta quantos robôs estão vivos e identifica o vencedor
                for i in range(ss.QTD_ROBOS):
                    if self.robots[i].status == b'V':
                        vivos += 1
                        vencedor_id = self.robots[i].ID
            
            # Se apenas um robô está vivo, define o vencedor e encerra o jogo
            if vivos <= 1:
                setFlagVencedor(self.flags, vencedor_id)
                setFlagGameOver(self.flags, 1)

    def mover(self):
        # Busca a bateria mais próxima se a energia estiver baixa
        bateria_mais_proxima = None
        menor_distancia = float('inf')
        for y in range(ss.HEIGHT):
            for x in range(ss.WIDTH):
                if self.get_grid(x, y) == "B":
                    # Calcula a distância Manhattan para a bateria
                    # A distância Manhattan é a soma das diferenças absolutas das coordenadas
                    distancia = abs(self.posicao_x - x) + abs(self.posicao_y - y)
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        bateria_mais_proxima = (x, y)
        
        dx, dy = 0, 0
        # Se a energia for baixa, busca a bateria
        if self.energia < 50 and bateria_mais_proxima:
            self.log.append(f"Robo {self.ID} com energia baixa ({self.energia}). Buscando bateria.")
            bateria_x, bateria_y = bateria_mais_proxima
            # Move-se na direção da bateria mais próxima
            # A lógica de movimento é baseada na direção da bateria
            if self.posicao_x < bateria_x: dx = 1
            elif self.posicao_x > bateria_x: dx = -1
            elif self.posicao_y < bateria_y: dy = 1
            elif self.posicao_y > bateria_y: dy = -1
        # Caso contrário, move-se aleatoriamente
        else:
            dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])

        self.mover_para(dx, dy)

    
    def mover_para(self, dx, dy):
        # Verifica se o robô está ativo e se a movimentação é válida
        if self.status != b'V' or (dx==0 and dy==0):
            return
        
        # Calcula a nova posição, garantindo que não saia dos limites do grid
        nova_posicao_x = max(0, min(ss.WIDTH - 1, self.posicao_x + dx))
        nova_posicao_y = max(0, min(ss.HEIGHT - 1, self.posicao_y + dy))

        # Adquire o lock do grid apenas para ler o destino, e o libera em seguida
        with self.grid_mutex:
            destino = self.get_grid(nova_posicao_x, nova_posicao_y)
        
        if destino.isdigit() and destino != str(self.ID):
            self.duelar(int(destino), nova_posicao_x, nova_posicao_y)
        
        # Se o destino for um espaço vazio, move o robô
        elif destino == "-":
            with self.grid_mutex:
                if self.get_grid(nova_posicao_x, nova_posicao_y) == "-":
                    self.set_grid(self.posicao_x, self.posicao_y, "-")
                    self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y
                    self.set_grid(self.posicao_x, self.posicao_y, str(self.ID))
                    self.energia -= 1
                    self.log.append(f"Robo {self.ID} se moveu para ({self.posicao_x}, {self.posicao_y}). Energia restante: {self.energia}.")
        # Se o destino for uma bateria, consome a bateria
        elif destino == "B":
            with self.grid_mutex: # Re-adquire o lock para uma operação rápida
                if self.get_grid(nova_posicao_x, nova_posicao_y) == "B":
                    self.set_grid(self.posicao_x, self.posicao_y, "-")
                    self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y
                    self.set_grid(self.posicao_x, self.posicao_y, str(self.ID))
                    self.energia = min(100, self.energia + 20)
                    self.log.append(f"Robo {self.ID} encontrou uma bateria e recarregou. Energia atual: {self.energia}.")
                    
        elif destino == "#": # BARREIRA #
                self.log.append(f"Robo {self.ID} encontrou uma barreira em ({nova_posicao_x}, {nova_posicao_y}) e não pôde se mover.")
                    
        
        # Atualiza o estado do robô na lista compartilhada
        if self.ID == 0:
            os.system("cls" if os.name == "nt" else "clear")
            print(f"Jogador {self.ID} | Energia: {self.energia} | Força: {self.forca}")
            gridFunctions.printGrid(self.grid)

    def duelar(self, outro_robo_id, x_duelo, y_duelo):
        # Pega a força e o status do outro robô
        with self.robots_mutex:
            outro_robo_forca = self.robots[outro_robo_id].forca
            outro_robo_status = self.robots[outro_robo_id].status
            outro_robo_energia = self.robots[outro_robo_id].energia

            # Verifica se o robo atual e o outro robo estao ativos
            if self.status != b"V" or outro_robo_status != b"V":
                return

            print(f"\nDUELO: Robô {self.ID} (F:{self.forca}) vs Robô {outro_robo_id} (F:{outro_robo_forca})")
            self.log.append(f"DUELO: Robô {self.ID} (F:{self.forca}) vs Robô {outro_robo_id} (F:{outro_robo_forca})")
            
            # Robo atual mais forte que o robo adversário
            poderRoboAtual = 2 * self.forca + self.energia
            poderOutroRobo = 2 * outro_robo_forca + outro_robo_energia
            if poderRoboAtual > poderOutroRobo:
                self.robots[outro_robo_id].status = b"M"
                with self.grid_mutex:
                    self.set_grid(self.posicao_x, self.posicao_y, "-") 
                    self.set_grid(x_duelo, y_duelo, str(self.ID))
                self.posicao_x, self.posicao_y = x_duelo, y_duelo
                self.log.append(f"Robo {self.ID} venceu o duelo contra o Robo {outro_robo_id}.")
            
            # Robo adversário mais forte que o robo atual
            elif poderRoboAtual < poderOutroRobo:
                self.status = b"M"
                self.robots[self.ID].status = b"M"
                with self.grid_mutex:
                    self.set_grid(self.posicao_x, self.posicao_y, "-")
                self.log.append(f"Robo {self.ID} foi derrotado pelo Robo {outro_robo_id}.")
            
            # Empate
            else:
                self.status = b"M"
                self.robots[self.ID].status = b"M"
                self.robots[outro_robo_id].status = b"M"
                with self.grid_mutex:
                    self.set_grid(self.posicao_x, self.posicao_y, "-")
                    self.set_grid(x_duelo, y_duelo, "-")
                self.log.append(f"Robo {self.ID} e Robo {outro_robo_id} empataram no duelo.")
        
        time.sleep(0.5) 
        self._check_game_over()

    # Rotina de percepção e ação do robô
    def sense_act(self):
        while True:
            with self.robots_mutex:
                if self.robots[self.ID].status != b'V': break
            if getFlagGameOver(self.flags) == 1: break
            self.mover()
            time.sleep(self.velocidade * 0.2) # Ajuste a velocidade do robô

    # Rotina de manutenção do robô
    def housekeeping(self):
        while True:
            with self.robots_mutex:
                # Verifica se o robô ainda está ativo
                if self.robots[self.ID].status != b'V': break
            # Verifica se o jogo acabou
            if getFlagGameOver(self.flags) == 1: break
            
            time.sleep(1)
            self.energia -= 1
            if self.energia <= 0:
                self.status = b"M"
                with self.robots_mutex:
                    self.robots[self.ID].status = b"M"
                    with self.grid_mutex:
                        self.set_grid(self.posicao_x, self.posicao_y, "-")
                self._check_game_over()
                break

    def iniciar(self):
        t_sense_act = threading.Thread(target=self.sense_act)
        t_housekeeping = threading.Thread(target=self.housekeeping)
        t_sense_act.start()
        t_housekeeping.start()
        t_sense_act.join()
        t_housekeeping.join()
        
        self.log.append(f"Robo {self.ID} finalizou suas atividades.")
        # Grava o log do robô em um arquivo
        with open(f"robot_{self.ID}_log.txt", "w", encoding="utf-8") as f:
            for entry in self.log:
                f.write(entry + "\n")
        

def processo_robo(ID, flags, robots_shared, robots_mutex, grid_mutex, flags_mutex, shm_name):
    shm = shared_memory.SharedMemory(name=shm_name)
    grid = shm.buf
    
    F = random.randint(1, 10) # Força 
    E = random.randint(10, 100) # Energia
    V = random.randint(1, 5) # Velocidade 

    with grid_mutex:
        while True:
            # Gera uma posição aleatória dentro dos limites do grid
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

    F = random.randint(1, 10) # Força do jogador
    E = 100
    V = random.randint(1, 5)

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
    gridFunctions.printGrid(robo.grid)

    while True:
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
            robo.status = b'M'
            with robots_mutex:
                robots_shared[robo.ID].status = b'M'
            break
    
    robo._check_game_over()
    t_housekeeping.join()
    shm.close()