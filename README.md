# Arena_dos_Processos

## 📂 Propósito

O propósito deste trabalho é a criação de um projeto que simula um jogo de luta entre robôs. 
Aplicaremos nosso aprendizado em Sistemas Operacionais 1 com respeito a threads, processos,
compartilhamento de memória entre outros conceitos importantes.

## 📂 Estrutura de Arquivos (Simplificada)
* `main.py`: Inicializa a memória compartilhada, cria os locks e lança os processos dos robôs.
* `viewer.py`: Componente de visualização do GRID em tempo real.
* `robots.py`: Contém a classe Robot (lógica de comportamento do robô) e a função que é o ponto de entrada para cada processo de robô.
* `gridFunctions.py`: Funções para inicializar e adicionar elementos ao GRID.
* `flagsFunctions.py`: Funções para gerenciar as flags do jogo.
* `shared_struct.py`: Define constantes e estruturas compartilhadas do projeto (ex: `WIDTH`, `HEIGHT`).

## 📂 Resumo instrucional - Arena dos Processos 

* Criar um jogo em modo texto, totalmente distribuído, usando processos e threads locais.
* Tabuleiro (40x20), barreiras, baterias e metadados dos robôs ficam em memória compartilhada.
* Cada robô sendo um processo que lê/escreve diretamente na memória compartilhada, usando mecanismos de sincronização.
* Duelos entre robôs adjacentes devem ser resolvidos dentro de uma região crítica protegida.
* Implementação mínima de 4 robôs independentes (um sendo o "robô do jogador").
* Cada robô tem duas threads: sense_act (decide a ação) e housekeeping (atualiza energia, log, locks).
* A memória compartilhada contém o GRID[40][20], um array de robôs (robots[]) e flags auxiliares.
* Locks obrigatórios incluem grid_mutex, robots_mutex e battery_mutex_k (um por bateria). A ordem de aquisição deve ser documentada.
* Atributos dos robôs: Força (1-10), Energia (10-100, consome 1 E por movimento, +20 E ao coletar, máx. 100), Velocidade (1-5, nº de células a tentar mover).
* Duelos: Poder = 2F+E. O robô com maior poder vence, o perdedor morre. Em caso de empate, ambos são destruídos. A negociação do duelo deve ser dentro do grid_mutex.
* Ciclo de vida do robô: Inicialização (primeiro processo gera o cenário), Loop principal (sense_act: snapshot, decide ação, adquire locks, executa ação, libera locks), e housekeeping (reduz energia, grava log, checa vitória).
* Componente de visualização que renderiza o GRID em tempo real a cada 50-200ms e termina quando o jogo acaba.



## 👥 Autores
* AMIN RICHAM SAMIR SOBH
* MARCO ANDRÉ SANTOS DA COSTA JÚNIOR
* THIAGO OLIVEIRA DA SILVA
* DAVI NUNES SANTOS 


