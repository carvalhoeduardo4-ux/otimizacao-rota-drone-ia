import heapq
import math
from grid import LIVRE, OBSTACULO, NO_FLY, DINAMICO

# Configurações de Voo do Drone
ALTURA_MINIMA = 1  
ALTURA_MAXIMA = 4

# Definição de Custos Energéticos (Função Objetivo)
CUSTO_HORIZONTAL = 1.5
CUSTO_SUBIDA = 3.0      # Maior custo conforme especificação
CUSTO_DESCIDA = 1.0     # Menor custo energético
PENALIDADE_NO_FLY = 50.0 # Alto custo para evitar, mas não impossível se for a única rota


class No:
    def __init__(self, posicao, g=0, h=0, pai=None):
        self.posicao = posicao
        self.g = g
        self.h = h
        self.f = g + h
        self.pai = pai

    def __lt__(self, outro):
        return self.f < outro.f


def heuristica(atual, destino):
    """
    Distância Euclidiana 3D como heurística admissível e consistente.
    """
    x1, y1, z1 = atual
    x2, y2, z2 = destino
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def obter_custo_movimento(dz, tipo_celula_destino):
    """
    Calcula o custo energético e de segurança baseado na direção e no tipo de célula.
    """
    #Custo Energético do Movimento
    if dz > 0:
        custo = CUSTO_SUBIDA
    elif dz < 0:
        custo = CUSTO_DESCIDA
    else:
        custo = CUSTO_HORIZONTAL

    #Penalidade de Segurança (Exposição a Regiões Restritas)
    if tipo_celula_destino == NO_FLY:
        custo += PENALIDADE_NO_FLY
        
    return custo


def obter_vizinhos(posicao, ambiente, origem_referencia=None, destino_referencia=None):
    x, y, z = posicao
    origem_referencia = origem_referencia if origem_referencia is not None else ambiente.origem
    destino_referencia = destino_referencia if destino_referencia is not None else ambiente.destino
    
    # As 6 direções permitidas: Frente, Trás, Esquerda, Direita, Subida, Descida
    movimentos = [
        (1, 0, 0), (-1, 0, 0),  # X
        (0, 1, 0), (0, -1, 0),  # Y
        (0, 0, 1), (0, 0, -1)   # Z
    ]

    vizinhos = []

    for dx, dy, dz in movimentos:
        nx, ny, nz = x + dx, y + dy, z + dz

        #Validação de Limites do Grid
        if not (0 <= nx < ambiente.tamanho_x and 
                0 <= ny < ambiente.tamanho_y and 
                0 <= nz < ambiente.tamanho_z):
            continue

        #Validação de Bloqueios Físicos Intransponíveis
        tipo_celula = ambiente.grid[nx, ny, nz]
        if tipo_celula in [OBSTACULO, DINAMICO]:
            continue

        #Regras de Altitude de Voo Cruzeiro (Segurança de Altitude)
        # Se NÃO for a célula exata de origem ou destino, o drone deve respeitar os limites operacionais
        if (nx, ny, nz) != origem_referencia and (nx, ny, nz) != destino_referencia:
            if nz < ALTURA_MINIMA or nz > ALTURA_MAXIMA:
                continue

        vizinhos.append((nx, ny, nz))

    return vizinhos


def reconstruir_caminho(no):
    caminho = []
    atual = no
    while atual is not None:
        caminho.append(atual.posicao)
        atual = atual.pai
    caminho.reverse()
    return caminho


def astar(ambiente, inicio=None, destino=None):
    inicio = ambiente.origem if inicio is None else inicio
    destino = ambiente.destino if destino is None else destino

    if inicio is None or destino is None:
        return None, 0  # Retorna o caminho vazio e 0 nós visitados

    aberto = []
    g_score = {inicio: 0.0}

    heapq.heappush(aberto, No(inicio, g=0.0, h=heuristica(inicio, destino)))
    visitados = set()

    while aberto:
        atual = heapq.heappop(aberto)

        if atual.posicao == destino:
            # SE ENCONTROU O DESTINO:
            # Retorna o caminho reconstruído E o total de nós que foram visitados
            return reconstruir_caminho(atual), len(visitados)

        if atual.posicao in visitados:
            continue

        visitados.add(atual.posicao)

        for v_pos in obter_vizinhos(atual.posicao, ambiente, inicio, destino):
            if v_pos in visitados:
                continue

            dz = v_pos[2] - atual.posicao[2]
            tipo_celula = ambiente.grid[v_pos[0], v_pos[1], v_pos[2]]
            
            custo_transicao = obter_custo_movimento(dz, tipo_celula)
            g_temporario = atual.g + custo_transicao

            if v_pos not in g_score or g_temporario < g_score[v_pos]:
                g_score[v_pos] = g_temporario
                h_custo = heuristica(v_pos, destino)
                
                novo_no = No(v_pos, g=g_temporario, h=h_custo, pai=atual)
                heapq.heappush(aberto, novo_no)

    # SE A FILA ACABAR E NÃO ACHAR CAMINHO:
    # Retorna None para o caminho E o total de nós que tentou explorar
    return None, len(visitados)