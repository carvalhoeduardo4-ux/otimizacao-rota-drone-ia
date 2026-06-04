# Otimização de Trajetória de UAV em Ambiente Urbano 3D
Trabalho prático de Inteligência Artificial focado no planejamento de rotas ótimas para Drones (UAVs) em cenários urbanos tridimensionais, comparando a eficiência de uma busca informada (**A***) com uma busca sistemática cega (**Busca em Largura - BFS**).

## Funcionalidades Atuais
- **Grid Urbano 3D:** Geração procedural de prédios fixos.
- **Modelagem Meteorológica:** Criação de zonas volumétricas de turbulência/vento forte (`NO_FLY`) que penalizam o consumo energético do drone.
- **Função Objetivo Física:** Custos diferenciados para subida (bateria pesada), descida (gravidade) e voo plano.
- **Painel Comparativo:** Tabela automática no console comparando nós explorados, tamanho do caminho e custo energético total de ambos os algoritmos.
- **Visualização Tridimensional:** Renderização interativa do mapa e das rotas usando `matplotlib`.

## Como Executar
1. Certifique-se de ter o Python 3.12+ instalado.
2. Instale as dependências necessárias:
   ```bash
   pip install matplotlib numpy

## Coleta Automática de Resultados
Para gerar várias amostras por cenário e alimentar a tabela do pôster, execute:
```bash
python coletar_dados.py --amostras 5 --cenarios cidade_limpa cidade_densa cidade_densa_vento_forte
```
Isso grava as amostras em `resultados.csv` sem abrir a visualização 3D.