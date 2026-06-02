import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from grid import (
    OBSTACULO,
    NO_FLY,
    ORIGEM,
    DESTINO,
    DINAMICO
)


def visualizar_ambiente_3d(ambiente, caminho=None):
    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_subplot(111, projection='3d')

    grid = ambiente.grid

    #PRÉDIOS E ZONAS DE VENTOS VOLUMÉTRICAS
    for x in range(ambiente.tamanho_x):
        for y in range(ambiente.tamanho_y):
            
            #Renderização dos Prédios (Colunas Laranjas)
            altura = 0
            for z in range(ambiente.tamanho_z):
                if grid[x, y, z] == OBSTACULO:
                    altura += 1
            
            if altura > 0:
                ax.bar3d(
                    x + 0.1, y + 0.1, 0,
                    0.8, 0.8, altura,
                    shade=True,
                    color="orange",
                    alpha=0.5, 
                    edgecolor="darkorange"
                )
                
            #Renderização das Zonas de Vento/No-Fly (Cubos Roxos Transparentes)
            for z in range(ambiente.tamanho_z):
                if grid[x, y, z] == NO_FLY:
                    ax.bar3d(
                        x + 0.05, y + 0.05, z + 0.05,
                        0.9, 0.9, 0.9,
                        shade=True,
                        color="purple",
                        alpha=0.12,
                        edgecolor="purple",
                        linewidth=0.2
                    )

    
    dinamico_x, dinamico_y, dinamico_z = [], [], []
    origem_pt, destino_pt = None, None

    for x in range(ambiente.tamanho_x):
        for y in range(ambiente.tamanho_y):
            for z in range(ambiente.tamanho_z):
                valor = grid[x, y, z]
                
                if valor == DINAMICO:
                    dinamico_x.append(x + 0.5)
                    dinamico_y.append(y + 0.5)
                    dinamico_z.append(z + 0.5)
                elif valor == ORIGEM:
                    origem_pt = (x + 0.5, y + 0.5, z)
                elif valor == DESTINO:
                    destino_pt = (x + 0.5, y + 0.5, z)

    if dinamico_x:
        ax.scatter(dinamico_x, dinamico_y, dinamico_z, marker="X", s=120, color="crimson", label="Obstáculo Dinâmico")

    if origem_pt:
        ax.scatter(origem_pt[0], origem_pt[1], origem_pt[2], marker="o", s=250, color="blue", label="Origem (Decolagem)")

    if destino_pt:
        ax.scatter(destino_pt[0], destino_pt[1], destino_pt[2], marker="o", s=250, color="green", label="Destino (Pouso)")

    #DESENHA ROTA DO DRONE
    if caminho is not None and len(caminho) > 0:
        xs, ys, zs = [], [], []
        for x, y, z in caminho:
            xs.append(x + 0.5)
            ys.append(y + 0.5)
            
            if (x, y, z) == ambiente.origem or (x, y, z) == ambiente.destino:
                zs.append(z)
            else:
                zs.append(z + 0.5)
            
        ax.plot(xs, ys, zs, linewidth=4, color="cyan", marker="o", markersize=6, label="Rota Otimizada A*")

    #CONFIGURAÇÕES VISUAIS E LEGENDAS
    ax.set_xlabel("Eixo Urbano X")
    ax.set_ylabel("Eixo Urbano Y")
    ax.set_zlabel("Altitude Z")
    ax.set_title("Simulação Urbana 3D: Otimização de Trajetória de UAV por Algoritmo A*", fontsize=12, pad=20)

    ax.set_box_aspect([ambiente.tamanho_x, ambiente.tamanho_y, ambiente.tamanho_z * 2.5])

    ax.set_xticks(range(0, ambiente.tamanho_x + 1, 5))
    ax.set_yticks(range(0, ambiente.tamanho_y + 1, 5))
    ax.set_zticks(range(0, ambiente.tamanho_z))

    
    handles, labels = ax.get_legend_handles_labels()
    
    patch_predio = mpatches.Patch(color='orange', alpha=0.5, label='Prédios (Fixos)')
    patch_vento = mpatches.Patch(color='purple', alpha=0.2, label='Zonas de Turbulência')
    
    handles.append(patch_predio)
    handles.append(patch_vento)
    
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.05, 1))

    plt.tight_layout()
    plt.show()