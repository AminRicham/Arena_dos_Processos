"""
FLAGS
init_done - indica se terminou o processo de inicio do jogo
vencedor - indidca o vencendor
Game over - indica se acabou
"""
def initFlags(flags):
    flags[0] = 0 
    flags[1] = -1
    flags[2] = 0

def getFlagInitDone(flags):
    return flags[0]

def setFlagInitDone(flags, data):
    flags[0] = data

def getFlagVencedor(flags):
    return flags[1]

def setFlagVencedor(flags, idWinner):
    flags[1] = idWinner

def getFlagGameOver(flags):
    return flags[2]

def setFlagGameOver(flags, data):
    flags[2] = data
    