import shared_struct as ss
def initFlags(flags, shm_buf):
    """
    Inicia o array de flags com localizações:
    flag[0] - Init_Done - indica se terminou o processo de inicio do jogo
    flag[1] - Vencedor - indica o vencendor
    flag[2] - Game over - indica se acabou
    Args:
        flags: array compartilhado das flags.
    """
    flags[0] = 0 
    flags[1] = -1
    flags[2] = 0
    shm_buf[ss.TOTAL_SIZE] = 0


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
    