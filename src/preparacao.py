"""Carregamento e preparação do CSV da PRF

O Pandas é usado aqui (leitura, filtragem e conversão de tipos)
A lógica de quem é "prioritário" vem das regras.
"""
import pandas as pd # type: ignore


def carregar_ocorrencias(caminho_csv, uf="MG"):
    """Lê o CSV da PRF e devolve só as ocorrências da UF indicada."""
    # O CSV da PRF usa ; como separador e codificação latin1
    df = pd.read_csv(caminho_csv, sep=";", encoding="latin1")

    # .copy() evita avisos do Pandas ao alterar colunas do recorte
    dados = df[df["uf"] == uf].copy()

    # km costuma vir com vírgula decimal, troca por ponto e converte
    # errors="coerce" transforma valores inválidos em NaN em vez de dar erro
    dados["km"] = pd.to_numeric(
        dados["km"].astype(str).str.replace(",", "."), errors="coerce"
    )
    dados["br"] = pd.to_numeric(dados["br"], errors="coerce")

    # Contagens de vítimas >> vazios viram 0, para poder comparar com > 0
    for col in ["mortos", "feridos_graves"]:
        dados[col] = pd.to_numeric(dados[col], errors="coerce").fillna(0).astype(int)

    # O id vira inteiro para usar como argumento dos fatos
    dados["id"] = dados["id"].astype(int)
    return dados
