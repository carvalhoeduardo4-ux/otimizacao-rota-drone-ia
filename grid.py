import numpy as np
import random

# Estados do Grid
LIVRE = 0
OBSTACULO = 1
NO_FLY = 2
ORIGEM = 3
DESTINO = 4
DINAMICO = 5


class Ambiente3D:

    def __init__(self, tamanho_x=20, tamanho_y=20, tamanho_z=5):
        self.tamanho_x = tamanho_x
        self.tamanho_y = tamanho_y
        self.tamanho_z = tamanho_z

        self.grid = np.zeros((tamanho_x, tamanho_y, tamanho_z), dtype=int)

        self.origem = None
        self.destino = None

    def gerar_predios(self, quantidade=40, altura_max=3):
        """
        Gera prédios a partir do solo (Z=0) até uma altura aleatória.
        """
        criados = 0
        tentativas = 0

        while criados < quantidade and tentativas < 2000:
            tentativas += 1
            x = random.randint(0, self.tamanho_x - 1)
            y = random.randint(0, self.tamanho_y - 1)
            
            
            altura = random.randint(1, altura_max)

            pode_criar = True
            for z in range(altura):
                if self.grid[x, y, z] != LIVRE:
                    pode_criar = False
                    break

            if pode_criar:
                for z in range(altura):
                    self.grid[x, y, z] = OBSTACULO
                criados += 1
                
    def gerar_zonas_restritas(self, quantidade=4, tamanho_zona=4):
        """
        Gera regiões volumétricas (ambientes com vento/turbulência).
        'quantidade' define quantas massas de ar instáveis existem.
        'tamanho_zona' define o tamanho do lado do cubo de vento.
        """
        import random
        
        from grid import LIVRE, NO_FLY 
        
        zonas_geradas = 0
        tentativas_maximas = 100  
        tentativas = 0

        while zonas_geradas < quantidade and tentativas < tentativas_maximas:
            tentativas += 1
            
            
            start_x = random.randint(0, max(0, self.tamanho_x - tamanho_zona))
            start_y = random.randint(0, max(0, self.tamanho_y - tamanho_zona))
            
        
            start_z = random.randint(1, 2) 

            blocos_pintados_nesta_zona = 0

            
            for x in range(start_x, start_x + tamanho_zona):
                for y in range(start_y, start_y + tamanho_zona):
                    
                    for z in range(start_z, min(self.tamanho_z, start_z + 2)):
                        
                        
                        if 0 <= x < self.tamanho_x and 0 <= y < self.tamanho_y and 0 <= z < self.tamanho_z:
                            
                            if self.grid[x, y, z] == LIVRE:
                                self.grid[x, y, z] = NO_FLY
                                blocos_pintados_nesta_zona += 1

            
            if blocos_pintados_nesta_zona > 0:
                zonas_geradas += 1
                
    def definir_origem_destino(self):
        """
        Define a origem e o destino do drone.
        """
        tentativas = 0
        origem = None
        while tentativas < 1000:
            
            x = random.randint(0, self.tamanho_x - 1)
            y = random.randint(0, self.tamanho_y - 1)
            pos_teste = (x, y, 0)

            if self.grid[pos_teste] == LIVRE:
                origem = pos_teste
                break
            tentativas += 1

        if origem == None:
            raise Exception("Não foi possível gerar uma origem válida (Grid muito denso)")

        tentativas = 0
        destino = None
        while tentativas < 1000:
            x = random.randint(0, self.tamanho_x - 1)
            y = random.randint(0, self.tamanho_y - 1)
            pos_teste = (x, y, 0)

            # Destino deve ser diferente da origem e estar livre
            if pos_teste != origem and self.grid[pos_teste] == LIVRE:
                destino = pos_teste
                break
            tentativas += 1

        if destino == None:
            raise Exception("Não foi possível gerar um destino válido (Grid muito denso)")

        self.origem = origem
        self.destino = destino

        
        self.grid[origem] = ORIGEM
        self.grid[destino] = DESTINO

    def adicionar_obstaculo_dinamico(self):
        # OBS: Deixado para o outro integrante implementar a lógica de tempo/movimento
        pass

    def mostrar_estatisticas(self):
        print("--- ESTATÍSTICAS DO AMBIENTE ---")
        print("Origem (Início):", self.origem)
        print("Destino (Fim):", self.destino)
        print("Prédios (Obstáculos Fixos):", np.sum(self.grid == OBSTACULO))
        print("Zonas No-Fly (Restritas):", np.sum(self.grid == NO_FLY))
        print("Obstáculos Dinâmicos:", np.sum(self.grid == DINAMICO))
        print("Espaço Livre Restante:", np.sum(self.grid == LIVRE))
        print("--------------------------------")

    def mostrar_camada(self, z):
        if 0 <= z < self.tamanho_z:
            print(f"\nVISUALIZAÇÃO DA CAMADA Z = {z} (Matriz Transposta para legibilidade X/Y)")
            
            print(self.grid[:, :, z].T)
        else:
            print("Nível de altitude inválido.")