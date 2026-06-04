import argparse
import os
import subprocess
import sys


SCENARIOS_PADRAO = ["cidade_limpa", "cidade_densa", "cidade_densa_vento_forte"]
CSV_PADRAO = "resultados.csv"


def obter_argumentos():
    parser = argparse.ArgumentParser(description="Executa várias amostras para a tarefa 2")
    parser.add_argument(
        "--amostras",
        type=int,
        default=5,
        help="Quantidade de execuções por cenário",
    )
    parser.add_argument(
        "--cenarios",
        nargs="*",
        choices=SCENARIOS_PADRAO,
        default=SCENARIOS_PADRAO,
        help="Cenários a executar",
    )
    parser.add_argument(
        "--manter-csv",
        action="store_true",
        help="Não apaga o CSV anterior antes de iniciar a coleta",
    )
    return parser.parse_args()


def limpar_csv(caminho_csv):
    if os.path.exists(caminho_csv):
        os.remove(caminho_csv)


def executar_amostras(amostras, cenarios, sem_visualizacao):
    python_executavel = sys.executable

    for cenario in cenarios:
        print(f"\n=== Coletando amostras para {cenario} ===")
        for indice in range(1, amostras + 1):
            print(f"Executando amostra {indice}/{amostras}...")

            comando = [python_executavel, "main.py", "--cenario", cenario]
            if sem_visualizacao:
                comando.append("--sem-visualizacao")

            resultado = subprocess.run(comando, capture_output=True, text=True)

            if resultado.returncode != 0:
                print(resultado.stdout)
                print(resultado.stderr)
                raise SystemExit(
                    f"Falha ao executar o cenário {cenario} na amostra {indice}."
                )

            print(resultado.stdout.strip())


def main():
    args = obter_argumentos()
    sem_visualizacao = True

    if not args.manter_csv:
        limpar_csv(CSV_PADRAO)

    executar_amostras(args.amostras, args.cenarios, sem_visualizacao)
    print(f"\nColeta concluída. As amostras foram gravadas em {CSV_PADRAO}.")


if __name__ == "__main__":
    main()