from collections import deque
from astar import obter_vizinhos

def bfs(ambiente, inicio=None, destino=None):
    """
    Implementação da Busca em Largura (BFS) para o ambiente 3D.
    Retorna o caminho encontrado e o número de nós explorados.
    """
    inicio = ambiente.origem if inicio is None else inicio
    destino = ambiente.destino if destino is None else destino

    if inicio is None or destino is None:
        return None, 0

    # Fila para armazenar (posicao_atual, caminho_ate_agora)
    fila = deque([(inicio, [inicio])])
    visitados = set([inicio])
    nos_explorados = 0

    while fila:
        atual, caminho = fila.popleft()
        nos_explorados += 1

        if atual == destino:
            return caminho, nos_explorados

        for vizinho in obter_vizinhos(atual, ambiente, inicio, destino):
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append((vizinho, caminho + [vizinho]))

    return None, nos_explorados