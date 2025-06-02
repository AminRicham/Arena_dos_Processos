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
    def __init__(self, ID, F, E, V, posicao_x, posicao_y, status):
        self.ID = ID
        self.forca = F
        self.energia = E
        self.velocidade = V
        self.posicao_x = posicao_x
        self.posicao_y = posicao_y
        self.status = status # Vivo ou morto
        
        # Adiciona o robô na grid se a posição estiver vazia
        with grid_mutex:
            GRID[self.y][self.x] = str(self.id)

    def mover(self):
        if self.energia <= 0:
            print(f"Robô {self.ID} sem energia para se mover.")
            return
        
        # Movimento aleatório do robo
        dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])  # Cima, baixo, esquerda, direita
        dx *= self.velocidade
        dy *= self.velocidade
        # Definindo nova posição
        nova_posicao_x = max(0, min(LARGURA_GRID - 1, self.posicao_x + dx))
        nova_posicao_y = max(0, min(ALTURA_GRID - 1, self.posicao_y + dy))
        print(f"Robo {self.ID} movendo de ({self.posicao_x}, {self.posicao_y}) para ({nova_posicao_x}, {nova_posicao_y})")
        
        

# testar a classe Robot
robo1 = Robot(ID=1, F=10, E=100, V=5, posicao_x=random.randint(0, 20), posicao_y=random.randint(0, 20), status="Vivo")
robo1.mover()
#print(vars(robo1))
    