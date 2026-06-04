from grid import Ambiente3D
from visualizacao import visualizar_ambiente_3d
from astar import astar, obter_custo_movimento
from bfs import bfs  
import copy
import argparse
import csv
import os
import time
from datetime import datetime


RESULTADOS_CSV = "resultados.csv"

CONFIGURACOES_CENARIO = {
    "cidade_limpa": {
        "predios": 25,
        "altura_max": 2,
        "zonas_restritas": 2,
        "tamanho_zona": 3,
        "descricao": "Cidade limpa",
    },
    "cidade_densa": {
        "predios": 80,
        "altura_max": 3,
        "zonas_restritas": 8,
        "tamanho_zona": 4,
        "descricao": "Cidade densa",
    },
    "cidade_densa_vento_forte": {
        "predios": 80,
        "altura_max": 3,
        "zonas_restritas": 5,
        "tamanho_zona": 5,
        "descricao": "Cidade densa e vento forte",
    },
}


def obter_argumentos():
    parser = argparse.ArgumentParser(description="Simulação 3D de rotas para A* e BFS")
    parser.add_argument(
        "--cenario",
        choices=CONFIGURACOES_CENARIO.keys(),
        default="cidade_densa",
        help="Seleciona a densidade do cenário para coleta de resultados",
    )
    parser.add_argument(
        "--sem-visualizacao",
        action="store_true",
        help="Executa a simulação sem abrir o gráfico 3D",
    )
    return parser.parse_args()


def registrar_resultado_csv(cenario, nos_astar, tempo_astar, custo_astar, passos_astar, nos_bfs, tempo_bfs, custo_bfs, passos_bfs, nos_tempo_real, replanejamentos):
    campos = [
        "data_hora",
        "cenario",
        "nos_astar",
        "tempo_astar_s",
        "custo_astar",
        "passos_astar",
        "nos_bfs",
        "tempo_bfs_s",
        "custo_bfs",
        "passos_bfs",
        "nos_tempo_real",
        "replanejamentos",
    ]

    arquivo_existe = os.path.exists(RESULTADOS_CSV)
    with open(RESULTADOS_CSV, mode="a", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        if not arquivo_existe:
            escritor.writeheader()

        escritor.writerow(
            {
                "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "cenario": cenario,
                "nos_astar": nos_astar,
                "tempo_astar_s": f"{tempo_astar:.6f}",
                "custo_astar": f"{custo_astar:.2f}",
                "passos_astar": passos_astar,
                "nos_bfs": nos_bfs,
                "tempo_bfs_s": f"{tempo_bfs:.6f}",
                "custo_bfs": f"{custo_bfs:.2f}",
                "passos_bfs": passos_bfs,
                "nos_tempo_real": nos_tempo_real,
                "replanejamentos": replanejamentos,
            }
        )


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


def simular_drone_principal_em_tempo_real(ambiente):
    """
    Registra a rota real do drone principal enquanto os drones dinâmicos se movem.
    """
    caminho_gravado = [ambiente.origem]
    posicao_atual = ambiente.origem
    nos_explorados_total = 0
    replanejamentos = 0
    esperas_consecutivas = 0
    limite_espera = 8
    limite_passos = ambiente.tamanho_x * ambiente.tamanho_y * 3
    passos = 0

    while posicao_atual != ambiente.destino and passos < limite_passos:
        passos += 1
        ambiente.atualizar_obstaculos_dinamicos(posicao_reservada=posicao_atual)

        caminho_atual, nos_explorados = astar(ambiente, inicio=posicao_atual, destino=ambiente.destino)
        nos_explorados_total += nos_explorados

        if not caminho_atual or len(caminho_atual) < 2:
            esperas_consecutivas += 1
            if esperas_consecutivas < limite_espera:
                continue
            break

        esperas_consecutivas = 0
        proximo_passo = caminho_atual[1]
        caminho_gravado.append(proximo_passo)
        posicao_atual = proximo_passo
        replanejamentos += 1

    return caminho_gravado, nos_explorados_total, replanejamentos

def main():
    args = obter_argumentos()
    configuracao = CONFIGURACOES_CENARIO[args.cenario]

    # 1. Inicializa o ambiente 3D
    ambiente = Ambiente3D(tamanho_x=20, tamanho_y=20, tamanho_z=5)

    print(f"Cenário selecionado: {configuracao['descricao']} ({args.cenario})")
    
    # Ordem de execução corrigida para evitar que prédios/zonas cubram a origem/destino
    ambiente.gerar_predios(quantidade=configuracao["predios"], altura_max=configuracao["altura_max"])
    ambiente.definir_origem_destino()
    ambiente.gerar_zonas_restritas(quantidade=configuracao["zonas_restritas"], tamanho_zona=configuracao["tamanho_zona"])
    ambiente.adicionar_obstaculo_dinamico()

    ambiente_tempo_real = copy.deepcopy(ambiente)
    rota_principal, nos_tempo_real, replanejamentos = simular_drone_principal_em_tempo_real(ambiente_tempo_real)

    ambiente.mostrar_estatisticas()
    print(f"Drone principal registrado em tempo real: {len(rota_principal)} passos e {replanejamentos} replanejamentos")
    print(f"Nós explorados durante o registro dinâmico: {nos_tempo_real}")

    # 2. Executa o A* (Busca Informada)
    inicio_astar = time.perf_counter()
    caminho_astar, nos_astar = astar(ambiente) 
    tempo_astar = time.perf_counter() - inicio_astar
    custo_astar = calcular_custo_total_rota(ambiente, caminho_astar) if caminho_astar else 0

    # 3. Executa a BFS (Busca Cega em Largura)
    inicio_bfs = time.perf_counter()
    caminho_bfs, nos_bfs = bfs(ambiente)
    tempo_bfs = time.perf_counter() - inicio_bfs
    custo_bfs = calcular_custo_total_rota(ambiente, caminho_bfs) if caminho_bfs else 0

    # 4. EXIBIÇÃO DA TABELA COMPARATIVA DE EFICIÊNCIA
    print("\n=======================================================")
    print("       METRICAS DE COMPARACAO: A* vs BUSCA EM LARGURA  ")
    print("=======================================================")
    print(f"{'Métrica':<30} | {'Algoritmo A*':<14} | {'Busca em Largura (BFS)':<15}")
    print("-" * 65)
    print(f"{'Nós Explorados (Eficiência)':<30} | {nos_astar:<14} | {nos_bfs:<15}")
    print(f"{'Tempo de Execução (s)':<30} | {tempo_astar:<14.6f} | {tempo_bfs:<15.6f}")
    print(f"{'Passos no Caminho':<30} | {len(caminho_astar) if caminho_astar else 0:<14} | {len(caminho_bfs) if caminho_bfs else 0:<15}")
    print(f"{'Custo Energético Total':<30} | {custo_astar:<14.2f} | {custo_bfs:<15.2f}")
    print("=======================================================")

    registrar_resultado_csv(
        args.cenario,
        nos_astar,
        tempo_astar,
        custo_astar,
        len(caminho_astar) if caminho_astar else 0,
        nos_bfs,
        tempo_bfs,
        custo_bfs,
        len(caminho_bfs) if caminho_bfs else 0,
        nos_tempo_real,
        replanejamentos,
    )

    # 5. Renderiza a visualização comparando A* e BFS
    if not args.sem_visualizacao and (caminho_astar or caminho_bfs):
        print("\nExibindo o gráfico tridimensional com A* e BFS...")
        visualizar_ambiente_3d(ambiente, caminho_astar, caminho_bfs)

if __name__ == "__main__":
    main()