"""transforma linhas do CSV em fatos lógicos

Este é o ponto onde os dados reais viram lógica, aqui só se registra
os fatos observados, nenhuma conclusão (severa, prioritaria...)
é criada aqui
"""
from collections import Counter


def atom(predicado, *args):
    #Cria um átomo
    return (predicado, *args)


def linha_para_fatos(row):
    #Converte uma linha do DataFrame em uma lista de fatos sobre a ocorrência
    o = int(row["id"])
    fatos = [atom("Ocorrencia", o)]       # toda ocorrência existe como fato

    # Vítimas >> contagens numéricas viram fatos de presença
    if row["mortos"] > 0:
        fatos.append(atom("TemVitimaFatal", o))
    if row["feridos_graves"] > 0:
        fatos.append(atom("TemFeridoGrave", o))

    # Condições do local, str(...).strip().lower() padroniza o texto antes de
    # comparar (ignora maiúsculas, espaços e valores vazios/NaN).
    if str(row["condicao_metereologica"]).strip().lower() == "chuva":
        fatos.append(atom("Chuva", o))
    if "curva" in str(row["tracado_via"]).lower():
        fatos.append(atom("Curva", o))
    if str(row["fase_dia"]).strip().lower() == "plena noite":
        fatos.append(atom("PlenaNoite", o))
    if str(row["tipo_pista"]).strip().lower() == "simples":
        fatos.append(atom("PistaSimples", o))
    if "frontal" in str(row["tipo_acidente"]).lower():
        fatos.append(atom("ColisaoFrontal", o))

    return fatos


def gerar_fatos(dados):
    #Gera o conjunto de fatos iniciais para todas as linhas do DataFrame
    # set: evita duplicatas e permite checar "o fato já existe?" rapidamente
    fatos = set()
    for _, row in dados.iterrows():
        fatos.update(linha_para_fatos(row))
    return fatos


def contar_predicados(fatos):
    """Conta quantos fatos existem por predicado

    Se um predicado importante aparecer com 0, o texto comparado em
    linha_para_fatos provavelmente difere do que está no CSV
    """
    return Counter(f[0] for f in fatos)
