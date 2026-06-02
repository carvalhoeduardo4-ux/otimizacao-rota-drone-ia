from grid import Ambiente3D
from visualizacao import visualizar_ambiente_3d
from astar import astar, obter_custo_movimento
from bfs import bfs  

def calcular_custo_total_rota(ambiente, caminho):
    """
    Calcula o custo real da rota com base na física de movimentação 
    e penalidades, atendendo à função objetivo do trabalho.
    """
    if not caminho or len(caminho) < 2:
        return 0.0
        
    custo_total = 0.0
    for i in range(len(caminho) - 1):
        atual = caminho[i]
        proximo = caminho[i+1]
        
        # Calcula a variação de altitude (Z) para saber se subiu, desceu ou plano
        dz = proximo[2] - atual[2]
        # Identifica o tipo de célula do destino do passo
        tipo_celula = ambiente.grid[proximo[0], proximo[1], proximo[2]]
        
        # Acumula o custo usando as regras de energia do A*
        custo_total += obter_custo_movimento(dz, tipo_celula)
        
    return custo_total

def main():
    # 1. Inicializa o ambiente 3D
    ambiente = Ambiente3D(tamanho_x=20, tamanho_y=20, tamanho_z=5)
    
    # Ordem de execução corrigida para evitar que prédios/zonas cubram a origem/destino
    ambiente.gerar_predios(quantidade=80, altura_max=3)
    ambiente.definir_origem_destino()
    ambiente.gerar_zonas_restritas(quantidade=8, tamanho_zona=4)
    ambiente.adicionar_obstaculo_dinamico()

    ambiente.mostrar_estatisticas()

    # 2. Executa o A* (Busca Informada)
    caminho_astar, nos_astar = astar(ambiente) 
    custo_astar = calcular_custo_total_rota(ambiente, caminho_astar) if caminho_astar else 0

    # 3. Executa a BFS (Busca Cega em Largura)
    caminho_bfs, nos_bfs = bfs(ambiente)
    custo_bfs = calcular_custo_total_rota(ambiente, caminho_bfs) if caminho_bfs else 0

    # 4. EXIBIÇÃO DA TABELA COMPARATIVA DE EFICIÊNCIA
    print("\n=======================================================")
    print("       METRICAS DE COMPARACAO: A* vs BUSCA EM LARGURA  ")
    print("=======================================================")
    print(f"{'Métrica':<25} | {'Algoritmo A*':<14} | {'Busca em Largura (BFS)':<15}")
    print("-" * 65)
    print(f"{'Nós Explorados (Eficiência)':<25} | {nos_astar:<14} | {nos_bfs:<15}")
    print(f"{'Passos no Caminho':<25} | {len(caminho_astar) if caminho_astar else 0:<14} | {len(caminho_bfs) if caminho_bfs else 0:<15}")
    print(f"{'Custo Energético Total':<25} | {custo_astar:<14.2f} | {custo_bfs:<15.2f}")
    print("=======================================================")

    # 5. Renderiza a visualização com o caminho do A*
    if caminho_astar:
        print("\nExibindo o gráfico tridimensional do caminho ótimo (A*)...")
        visualizar_ambiente_3d(ambiente, caminho_astar)

if __name__ == "__main__":
    main()