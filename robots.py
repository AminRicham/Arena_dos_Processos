from random import randint

# Constantes para pegar do grid
# Testes
LARGURA_GRID = 20 
ALTURA_GRID = 20


class Robot:
    def __init__(self, ID, F, E, V, posicao_x, posicao_y, status):
        self.ID = ID
        self.forca = F
        self.energia = E
        self.velocidade = V
        self.posicao_x = posicao_x
        self.posicao_y = posicao_y
        self.status = status # Vivo ou morto

    

    