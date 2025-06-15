import random
import multiprocessing as mp
import threading
import shared_struct as ss
import gridFunctions
from flagsFunctions import getFlagGameOver
import time
from teclado import ler_tecla

# Criação dos locks mutex
grid_mutex = mp.Lock()


class Robot:
    def __init__(self, ID, F, E, V, posicao_x, posicao_y, status, grid, flags, robots_shared, robots_mutex, grid_mutex):
        self.ID = ID
        self.forca = F
        self.energia = E
        self.velocidade = V
        self.posicao_x = posicao_x
        self.posicao_y = posicao_y
        self.status = status # Vivo ou morto
        self.log = [] # Log de ações do robô
        self.grid = grid
        self.flags = flags
        self.robots = robots_shared  # Lista de robôs compartilhada
        self.robots_mutex = robots_mutex
        self.grid_mutex = grid_mutex  # Mutex para proteger o grid
        
        # Adiciona o robô na grid se a posição estiver vazia
        with self.grid_mutex: # Protegendo o grid
            self.set_grid(self.posicao_x, self.posicao_y, str(self.ID))

    def get_index(self, x, y):
        """Calcula o índice do grid baseado na posição x e y."""
        return y * ss.WIDTH + x
    
    def get_grid(self, x, y):
        """Obtém o valor do grid na posição (x, y)."""
        return self.grid[self.get_index(x, y)]
    
    def set_grid(self, x, y, value):
        """Define o valor do grid na posição (x, y)."""
        index = self.get_index(x, y)
        self.grid[index] = value
        
    def mover(self):
        if self.energia <= 0 or self.status != b"V":
            print(f"Robô {self.ID} sem energia ou morto.")
            return
        
        # Buscar bateria mais proxima
        bateria_mais_proxima = None
        menor_distancia = float('inf')
        for y in range(ss.HEIGHT):
            for x in range(ss.WIDTH):
                if self.get_grid(x, y) == "B":
                    distancia = abs(self.posicao_x - x) + abs(self.posicao_y - y)
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        bateria_mais_proxima = (x, y)
        
        # Se encontrou uma bateria, move-se em direção a ela
        if bateria_mais_proxima:
            bateria_x, bateria_y = bateria_mais_proxima
            dx = 0
            dy = 0
            # Verifica a direção para se mover em direção à bateria
            # Se o x da bateria for maior que o x do robô, move para a direita (dx = 1)
            if self.posicao_x < bateria_x:
                dx = 1
            # Se o x da bateria for menor que o x do robô, move para a esquerda (dx = -1)
            elif self.posicao_x > bateria_x:
                dx = -1
            # se for 0, quer dizer que o robô está na mesma linha da bateria
            if dx == 0:
                if self.posicao_y < bateria_y:
                    dy = 1
                elif self.posicao_y > bateria_y:
                    dy = -1
        else:
            # Movimento aleatório se não houver bateria próxima
            dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
        
        nova_posicao_x = max(0, min(ss.WIDTH - 1, self.posicao_x + dx))
        nova_posicao_y = max(0, min(ss.HEIGHT - 1, self.posicao_y + dy))
        
        # Movimento aleatório do robo
        #dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])  # Cima, baixo, esquerda, direita
        # Definindo nova posição
        #nova_posicao_x = max(0, min(ss.WIDTH - 1, self.posicao_x + dx)) # Verificação para não sair do grid e chegar no ultimo bloco
        #nova_posicao_y = max(0, min(ss.HEIGHT - 1, self.posicao_y + dy))
        
        with self.grid_mutex:
            # Para onde o robo quer se mover
            destino = self.get_grid(nova_posicao_x, nova_posicao_y)
            if destino == "-":
                # Atualiza a posição do robô na grid
                self.set_grid(self.posicao_x, self.posicao_y, "-") # Limpa a posição antiga
                self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y # Define a nova posição do robô
                self.set_grid(self.posicao_x, self.posicao_y, str(self.ID)) # Atualiza a grid com a nova posição do robô (0, 5, id) - (x, y, id)
                self.energia -= 1 # 1 de energia por movimento
                self.log.append(f"Robo {self.ID} se moveu para ({self.posicao_x}, {self.posicao_y}). Energia restante: {self.energia}.")
            
            elif destino == "B": # RAIO ⚡
                self.set_grid(self.posicao_x, self.posicao_y, "-") # Limpa a posição antiga
                self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y # Define a nova posição do robô
                self.set_grid(self.posicao_x, self.posicao_y, str(self.ID)) # Atualiza a grid com a nova posição do robô
                self.energia = min(100, self.energia + 20) # Recarrega a energia garantindo que não ultrapasse 100
                self.log.append(f"Robo {self.ID} encontrou uma bateria e recarregou. Energia atual: {self.energia}.")
                
            
            elif destino == "#": # BARREIRA #
                self.log.append(f"Robo {self.ID} encontrou uma barreira em ({nova_posicao_x}, {nova_posicao_y}) e não pôde se mover.")
                
            elif destino.isdigit() and destino != str(self.ID): # Se a posição já estiver ocupada por outro robô
                self.duelar(int(destino))
                
    def mover_para(self,dx,dy):
        nova_posicao_x = max(0, min(ss.WIDTH - 1, self.posicao_x + dx))
        nova_posicao_y = max(0, min(ss.HEIGHT - 1, self.posicao_y + dy))
        
        with self.grid_mutex:
            # Para onde o robo quer se mover
            destino = self.get_grid(nova_posicao_x, nova_posicao_y)
            if destino == "-":
                # Atualiza a posição do robô na grid
                self.set_grid(self.posicao_x, self.posicao_y, "-") # Limpa a posição antiga
                self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y # Define a nova posição do robô
                self.set_grid(self.posicao_x, self.posicao_y, str(self.ID)) # Atualiza a grid com a nova posição do robô (0, 5, id) - (x, y, id)
                self.energia -= 1 # 1 de energia por movimento
                self.log.append(f"Jogador {self.ID} se moveu para ({self.posicao_x}, {self.posicao_y}). Energia restante: {self.energia}.")
            
            elif destino == "B": # RAIO ⚡
                self.set_grid(self.posicao_x, self.posicao_y, "-") # Limpa a posição antiga
                self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y # Define a nova posição do robô
                self.set_grid(self.posicao_x, self.posicao_y, str(self.ID)) # Atualiza a grid com a nova posição do robô
                self.energia = min(100, self.energia + 20) # Recarrega a energia garantindo que não ultrapasse 100
                self.log.append(f"Jogador {self.ID} encontrou uma bateria e recarregou. Energia atual: {self.energia}.")
                
            elif destino == "#": # BARREIRA #
                self.log.append(f"Jogador {self.ID} encontrou uma barreira em ({nova_posicao_x}, {nova_posicao_y}) e não pôde se mover.")
                
            elif destino.isdigit() and destino != str(self.ID): # Se a posição já estiver ocupada por outro robô
                self.duelar(int(destino))

    def duelar(self, outro_robo_id):
        outro_robo = self.robots[outro_robo_id]
        
        # Confirmar que ainda estão vivos
        if self.status != b"V" or outro_robo.status != b"V":
            return
        
        # Lógica de duelo
        if self.forca > outro_robo.forca:
            self.log.append(f"Robo {self.ID} venceu o duelo contra Robo {outro_robo_id}.")
            with self.robots_mutex:
                outro_robo.status = b"M"
            with self.grid_mutex:
                self.set_grid(outro_robo.posicao_x, outro_robo.posicao_y, "-")
        
        elif self.forca < outro_robo.forca:
            self.log.append(f"Robo {self.ID} perdeu o duelo contra Robo {outro_robo_id}.")
            self.status = b"M"
            with self.robots_mutex:
                self.robots[self.ID].status = b"M"
            with self.grid_mutex:
                self.set_grid(self.posicao_x, self.posicao_y, "-")
        
        else: 
            self.log.append(f"Robo {self.ID} e Robo {outro_robo_id} empataram no duelo.")
            self.status = b"M"
            with self.robots_mutex:
                outro_robo.status = b"M"
                self.robots[self.ID].status = b"M"
            with self.grid_mutex:
                self.set_grid(self.posicao_x, self.posicao_y, "-")
                self.set_grid(outro_robo.posicao_x, outro_robo.posicao_y, "-")
            
    def sense_act(self):
        """Método para o robô sentir o ambiente e agir."""
        while self.status == b"V" and getFlagGameOver(self.flags) == 0:
            self.mover()
            tempo_espera = self.velocidade * 0.2
            time.sleep(tempo_espera)  # Simula o tempo de espera baseado na velocidade do robô
    
    def housekeeping(self):
        """Método para o robô realizar tarefas de manutenção."""
        while self.status == b"V" and getFlagGameOver(self.flags) == 0:
            self.energia -= 1
            if self.energia <= 0:
                self.status = b"M"
                with self.grid_mutex:
                    self.set_grid(self.posicao_x, self.posicao_y, "-")
                self.log.append(f"Robo {self.ID} ficou sem energia e foi desligado.")
            time.sleep(1)
            
    def iniciar(self):
        t1 = threading.Thread(target=self.sense_act)
        t2 = threading.Thread(target=self.housekeeping)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        self.log.append(f"Robo {self.ID} finalizou suas atividades.")
        for linha in self.log:
            print(linha)

def processo_robo(ID, grid, flags, robots_shared, robots_mutex, grid_mutex):
    """Função para iniciar o processo do robô."""
    # Inicializa o robô com valores aleatórios
    F = random.randint(1, 10)  # Força
    E = random.randint(50, 100)  # Energia
    V = random.randint(1, 5)  # Velocidade
    posicao_x = random.randint(0, ss.WIDTH - 1)
    posicao_y = random.randint(0, ss.HEIGHT - 1)
    
    robo = Robot(ID, F, E, V, posicao_x, posicao_y, b"V", grid, flags, robots_shared, robots_mutex, grid_mutex)
    robo.iniciar()
    
def processo_jogador(ID, grid, flags, robots_shared, robots_mutex, grid_mutex):
    """Função para iniciar o processo do robô jogador."""
    # Inicializa o robô com valores aleatórios
    F = random.randint(1, 10)  # Força
    E = 100  # Energia == 100 por conta do dinamismo do jogador
    V = 1  # Velocidade == 1 por conta do dinamismo do jogador
    posicao_x = random.randint(0, ss.WIDTH - 1)
    posicao_y = random.randint(0, ss.HEIGHT - 1)
    
    robo = Robot(ID, F, E, V, posicao_x, posicao_y, b"V", grid, flags, robots_shared, robots_mutex, grid_mutex)
    
    controles = {
        'w':(0, -1),
        's':(0,1),
        'a':(-1,0),
        'd':(1,0)
    }
    t_houseKeeping = threading.Thread(target = robo.housekeeping)
    t_houseKeeping.start()

    print("Controle ativado, use W A S D para se moviementar. Q para sair")

    while robo.status == b"V" and getFlagGameOver(flags) == 0:
        tecla = ler_tecla().lower()
        if tecla in controles:
            dx, dy = controles[tecla]
            robo.mover_para(dx,dy)
        elif tecla == 'q':
            print("Adeus!!")
            break
        else:
            print("Comando inválido")
    t_houseKeeping.join()
