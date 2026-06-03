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
        self.drones_dinamicos = []

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

    def _posicao_disponivel_para_drone(self, posicao, permitir_no_fly=False):
        if posicao == self.origem or posicao == self.destino:
            return False

        valor_atual = self.grid[posicao]
        if valor_atual in [OBSTACULO, ORIGEM, DESTINO, DINAMICO]:
            return False

        if not permitir_no_fly and valor_atual == NO_FLY:
            return False

        return True

    def _sortear_posicao_dinamica(self, permitir_no_fly=False, posicoes_bloqueadas=None):
        posicoes_bloqueadas = posicoes_bloqueadas or set()

        for _ in range(500):
            x = random.randint(0, self.tamanho_x - 1)
            y = random.randint(0, self.tamanho_y - 1)
            z = random.randint(0, self.tamanho_z - 1)
            posicao = (x, y, z)

            if posicao in posicoes_bloqueadas:
                continue

            if self._posicao_disponivel_para_drone(posicao, permitir_no_fly=permitir_no_fly):
                return posicao

        return None

    def _nova_rota_dinamica(self, posicao_atual, posicoes_bloqueadas=None):
        from astar import astar

        posicoes_bloqueadas = posicoes_bloqueadas or set()

        destino = self._sortear_posicao_dinamica(permitir_no_fly=True, posicoes_bloqueadas=posicoes_bloqueadas | {posicao_atual})
        if destino is None:
            return None

        caminho, _ = astar(self, inicio=posicao_atual, destino=destino)
        if caminho and len(caminho) > 1:
            return {"origem": posicao_atual, "destino": destino, "caminho": caminho[1:]}

        return None

    def adicionar_obstaculo_dinamico(self):
        """
        Cria drones dinâmicos que se deslocam entre pontos aleatórios.

        A origem desses drones pode ser gerada dentro de zonas NO_FLY para
        representar aeronaves que já estavam em voo quando a simulação começou.
        """
        volume = self.tamanho_x * self.tamanho_y * self.tamanho_z
        quantidade = max(1, min(12, volume // 300))

        criados = 0
        tentativas = 0
        tentativas_maximas = quantidade * 40
        posicoes_ocupadas = {self.origem, self.destino}

        while criados < quantidade and tentativas < tentativas_maximas:
            tentativas += 1

            origem_dron = self._sortear_posicao_dinamica(permitir_no_fly=True, posicoes_bloqueadas=posicoes_ocupadas)
            if origem_dron is None:
                break

            destino_dron = self._sortear_posicao_dinamica(permitir_no_fly=True, posicoes_bloqueadas=posicoes_ocupadas | {origem_dron})
            if destino_dron is None or destino_dron == origem_dron:
                continue

            self.drones_dinamicos.append({
                "posicao": origem_dron,
                "destino": destino_dron,
                "celula_base": self.grid[origem_dron],
                "trajeto": [origem_dron],
            })
            self.grid[origem_dron] = DINAMICO
            posicoes_ocupadas.add(origem_dron)
            posicoes_ocupadas.add(destino_dron)
            criados += 1

        return criados

    def atualizar_obstaculos_dinamicos(self, posicao_reservada=None):
        """
        Move cada drone dinâmico um passo por vez.

        Quando um drone chega ao destino, ele recebe uma nova rota para continuar
        em movimento durante a simulação.
        """
        if not self.drones_dinamicos:
            return 0

        movimentos_realizados = 0
        posicoes_reservadas = {posicao_reservada} if posicao_reservada is not None else set()

        for drone in self.drones_dinamicos:
            posicao_atual = drone["posicao"]

            if posicao_atual == drone["destino"]:
                nova_rota = self._nova_rota_dinamica(posicao_atual, posicoes_bloqueadas=posicoes_reservadas | {posicao_atual})
                if nova_rota is not None:
                    drone["destino"] = nova_rota["destino"]
                    drone["caminho"] = nova_rota["caminho"]
                else:
                    drone["caminho"] = []

            caminho = drone.get("caminho", [])
            if not caminho:
                caminho = []
                from astar import astar

                caminho_total, _ = astar(self, inicio=posicao_atual, destino=drone["destino"])
                if caminho_total and len(caminho_total) > 1:
                    caminho = caminho_total[1:]
                drone["caminho"] = caminho

            if not caminho:
                continue

            proximo = caminho[0]
            if proximo in posicoes_reservadas:
                continue

            valor_base_atual = drone.get("celula_base", LIVRE)
            if self.grid[posicao_atual] == DINAMICO:
                self.grid[posicao_atual] = valor_base_atual

            drone["celula_base"] = self.grid[proximo]
            self.grid[proximo] = DINAMICO
            drone["posicao"] = proximo
            drone["caminho"] = caminho[1:]
            drone.setdefault("trajeto", []).append(proximo)
            movimentos_realizados += 1

        return movimentos_realizados

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