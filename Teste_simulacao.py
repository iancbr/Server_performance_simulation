import heapq
import random
import numpy as np

# Parâmetros globais
LAMBDA = 2  # Taxa de chegada (jobs/seg)
AQUECIMENTO_JOBS = 10000  # warm up
MEDICAO_JOBS = 10000

# Situação 1: Tempos de serviço determinísticos
TEMPOS_DETERMINISTICOS = {
    1: 0.4,  # Servidor 1
    2: 0.6,  # Servidor 2
    3: 0.95,  # Servidor 3
}

# Função para geração de tempos de serviço
def tempo_servico(servidor, situacao):
    if situacao == 1:
        return TEMPOS_DETERMINISTICOS[servidor]
    elif situacao == 2:
        intervalos = {1: (0.1, 0.7), 2: (0.1, 1.1), 3: (0.1, 1.8)}
        return random.uniform(*intervalos[servidor])
    elif situacao == 3:
        medias = {1: 0.4, 2: 0.6, 3: 0.95}
        return np.random.exponential(medias[servidor])

# Inicialização do heap e métricas
fila_eventos = []  # Heap de eventos
tempos_no_sistema = []  # Lista de tempos no sistema para métricas
id_job = 0  # Identificador único de jobs

# Função para adicionar eventos ao heap
def adicionar_evento(heap, tempo, tipo_evento, servidor=None, job=None):
    heapq.heappush(heap, (tempo, tipo_evento, servidor, job))

# Inicializar chegada do primeiro job
def inicializar_simulacao():
    adicionar_evento(fila_eventos, np.random.exponential(1 / LAMBDA), "chegada")

# Simulação
def simular(situacao):
    global id_job
    tempo_atual = 0
    filas = {1: [], 2: [], 3: []}  # Filas dos servidores
    em_servico = {1: None, 2: None, 3: None}  # Job em serviço por servidor
    chegadas = {}  # Registrar tempo de chegada de cada job

    while len(tempos_no_sistema) < MEDICAO_JOBS:
        tempo, tipo_evento, servidor, job = heapq.heappop(fila_eventos)
        tempo_atual = tempo

        if tipo_evento == "chegada":
            id_job += 1
            chegadas[id_job] = tempo_atual
            filas[1].append(id_job)
            adicionar_evento(fila_eventos, tempo_atual + np.random.exponential(1 / LAMBDA), "chegada")

            if em_servico[1] is None:
                proximo_job = filas[1].pop(0)
                em_servico[1] = proximo_job
                duracao_servico = tempo_servico(1, situacao)
                adicionar_evento(fila_eventos, tempo_atual + duracao_servico, "saida", 1, proximo_job)

        elif tipo_evento == "saida":
            if servidor == 1:
                em_servico[1] = None
                proximo_servidor = 2 if random.random() < 0.5 else 3
                filas[proximo_servidor].append(job)

                if em_servico[proximo_servidor] is None:
                    proximo_job = filas[proximo_servidor].pop(0)
                    em_servico[proximo_servidor] = proximo_job
                    duracao_servico = tempo_servico(proximo_servidor, situacao)
                    adicionar_evento(fila_eventos, tempo_atual + duracao_servico, "saida", proximo_servidor, proximo_job)

                if filas[1]:
                    proximo_job = filas[1].pop(0)
                    em_servico[1] = proximo_job
                    duracao_servico = tempo_servico(1, situacao)
                    adicionar_evento(fila_eventos, tempo_atual + duracao_servico, "saida", 1, proximo_job)

            elif servidor == 2:
                em_servico[2] = None
                if random.random() < 0.2:
                    filas[2].append(job)
                else:
                    if job > AQUECIMENTO_JOBS:
                        tempos_no_sistema.append(tempo_atual - chegadas[job])

                if filas[2]:
                    proximo_job = filas[2].pop(0)
                    em_servico[2] = proximo_job
                    duracao_servico = tempo_servico(2, situacao)
                    adicionar_evento(fila_eventos, tempo_atual + duracao_servico, "saida", 2, proximo_job)

            elif servidor == 3:
                em_servico[3] = None
                if job > AQUECIMENTO_JOBS:
                    tempos_no_sistema.append(tempo_atual - chegadas[job])

                if filas[3]:
                    proximo_job = filas[3].pop(0)
                    em_servico[3] = proximo_job
                    duracao_servico = tempo_servico(3, situacao)
                    adicionar_evento(fila_eventos, tempo_atual + duracao_servico, "saida", 3, proximo_job)

# Função para rodar a simulação várias vezes
def rodar_simulacoes(situacao, n_execucoes):
    medias_resultados = []
    desvios_resultados = []

    for _ in range(n_execucoes):
        tempos_no_sistema.clear()
        fila_eventos.clear()
        id_job = 0
        inicializar_simulacao()
        simular(situacao)
        medias_resultados.append(np.mean(tempos_no_sistema))
        desvios_resultados.append(np.std(tempos_no_sistema))

    media_geral = np.mean(medias_resultados)
    desvio_geral = np.mean(desvios_resultados)
    return media_geral, desvio_geral

# Executar as simulações
n_execucoes = 10  # Número de execuções para cada situação
for situacao in [1, 2, 3]:
    tempo_medio, desvio_padrao = rodar_simulacoes(situacao, n_execucoes)
    print(f"Simulação - Situação {situacao}")
    print(f"Tempo médio no sistema (média das execuções): {tempo_medio}")
    print(f"Desvio padrão do tempo no sistema (média das execuções): {desvio_padrao}")
    print()
