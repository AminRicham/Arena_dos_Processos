import random
import multiprocessing as mp
import shared_struct as ss

# Criação dos locks mutex
grid_mutex = mp.Lock()

# Constantes para pegar do grid
# Testes | Alterar para pegar do grid
LARGURA_GRID = 20 
ALTURA_GRID = 20

# Simulação de grid 
GRID = [["-" for _ in range(LARGURA_GRID)] for _ in range(ALTURA_GRID)]

class Robot:
    def __init__(self, ID, F, E, V, posicao_x, posicao_y, status, grid, flags):
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
        
        # Adiciona o robô na grid se a posição estiver vazia
        with grid_mutex: # Protegendo o grid
            self.set_grid(self.x, self.y, str(self.ID))

    def get_index(self, x, y):
        """Calcula o índice do grid baseado na posição x e y."""
        return y * LARGURA_GRID + x
    
    def get_grid(self, x, y):
        """Obtém o valor do grid na posição (x, y)."""
        return self.grid[self.get_index(x, y)].decode()
    
    def set_grid(self, x, y, value):
        """Define o valor do grid na posição (x, y)."""
        index = self.get_index(x, y)
        self.grid[index] = value.encode()
        
    def mover(self):
        if self.energia <= 0 or self.status != "Vivo":
            print(f"Robô {self.ID} sem energia ou morto.")
            return
        
        # Movimento aleatório do robo
        dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])  # Cima, baixo, esquerda, direita
        dx *= self.velocidade
        dy *= self.velocidade
        # Definindo nova posição
        nova_posicao_x = max(0, min(ss.HEIGHT - 1, self.posicao_x + dx)) # Verificação para não sair do grid e chegar no ultimo bloco
        nova_posicao_y = max(0, min(ss.WIDTH - 1, self.posicao_y + dy))
        
        with grid_mutex:
            # Para onde o robo quer se mover
            destino = self.get_grid(nova_posicao_x, nova_posicao_y)
            if destino == "-":
                # Atualiza a posição do robô na grid
                self.set_grid(self.posicao_x, self.posicao_y, "-") # Limpa a posição antiga
                self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y # Define a nova posição do robô
                self.set_grid(self.posicao_x, self.posicao_y, str(self.ID)) # Atualiza a grid com a nova posição do robô (0, 5, id) - (x, y, id)
                
                self.energia -= 1 # 1 de energia por movimento
                self.log.append(f"Robo {self.ID} se moveu para ({self.posicao_x}, {self.posicao_y}). Energia restante: {self.energia}.")
            
            elif destino == "\U000026A1": # RAIO ⚡
                self.set_grid(self.posicao_x, self.posicao_y, "-") # Limpa a posição antiga
                self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y # Define a nova posição do robô
                self.set_grid(self.posicao_x, self.posicao_y, str(self.ID)) # Atualiza a grid com a nova posição do robô
                self.energia = min(100, self.energia + 20) # Recarrega a energia garantindo que não ultrapasse 100
                self.log.append(f"Robo {self.ID} encontrou uma bateria e recarregou. Energia atual: {self.energia}.")
            
            elif destino == "#": # BARREIRA #
                self.log.append(f"Robo {self.ID} encontrou uma barreira em ({nova_posicao_x}, {nova_posicao_y}) e não pôde se mover.")
                
            elif destino.isdigit() and destino != str(self.ID): # Se a posição já estiver ocupada por outro robô
                self.duelar(int(destino))
                
    def mostrar_log(self):
        print(f"Log do Robô {self.ID}:")
        for acao in self.log:
            print(acao)

# testar a classe Robot
robo1 = Robot(ID=1, F=10, E=100, V=5, posicao_x=random.randint(0, 19), posicao_y=random.randint(0, 19), status="Vivo")
robo1.mover()
robo1.mostrar_log()
#print(vars(robo1))
    