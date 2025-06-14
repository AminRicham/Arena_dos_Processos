import sys
#Se for windowns importa mscrt
if sys.platform.startswith('win'):
    import msvcrt
    
    def ler_tecla():
        return msvcrt.getch().decode("utf-8")
else:
    import tty, termios
    def ler_tecla():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch