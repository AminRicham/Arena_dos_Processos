import random
import multiprocessing as mp

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
        if self.energia <= 0:
            print(f"Robô {self.ID} sem energia para se mover.")
            return
        
        # Movimento aleatório do robo
        dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])  # Cima, baixo, esquerda, direita
        dx *= self.velocidade
        dy *= self.velocidade
        # Definindo nova posição
        nova_posicao_x = max(0, min(LARGURA_GRID - 1, self.posicao_x + dx)) # Verificação para não sair do grid e chegar no ultimo bloco
        nova_posicao_y = max(0, min(ALTURA_GRID - 1, self.posicao_y + dy))
        
        with grid_mutex:
            if GRID[nova_posicao_x][nova_posicao_y] == "-":
                # Atualiza a posição do robô na grid
                GRID[self.posicao_x][self.posicao_y] = "-" # Limpa a posição antiga
                GRID[nova_posicao_x][nova_posicao_y] = str(self.ID) # Define a nova posição do robô
                self.log.append(f"Robo {self.ID} movendo de ({self.posicao_x}, {self.posicao_y}) para ({nova_posicao_x}, {nova_posicao_y})")
                self.posicao_x, self.posicao_y = nova_posicao_x, nova_posicao_y
                self.energia -= 1
                self.log.append(f"{vars(self)}")
            else:
                self.log.append(f"Robo {self.ID} tentou se mover para ({nova_posicao_x}, {nova_posicao_y}), mas a posição já está ocupada.")
    
    def mostrar_log(self):
        print(f"Log do Robô {self.ID}:")
        for acao in self.log:
            print(acao)

# testar a classe Robot
robo1 = Robot(ID=1, F=10, E=100, V=5, posicao_x=random.randint(0, 19), posicao_y=random.randint(0, 19), status="Vivo")
robo1.mover()
robo1.mostrar_log()
#print(vars(robo1))
    