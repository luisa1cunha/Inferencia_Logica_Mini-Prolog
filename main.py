"""Executa as etapas 1 a 3: dados -> fatos -> forward chaining -> consultas."""
import argparse

from src.fatos import contar_predicados, gerar_fatos
from src.motor_logico import consultar_variavel, forward_chain
from src.preparacao import carregar_ocorrencias
from src.regras import REGRAS


def main():
    # Permite informar o caminho do CSV pela linha de comando
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/datatran2025.csv",
                        help="caminho do CSV de acidentes da PRF")
    args = parser.parse_args()

    # carregar e filtrar (apenas MG)
    mg = carregar_ocorrencias(args.csv)
    print("Ocorrências em MG:", mg.shape)

    # dados reais -> fatos lógicos
    fatos_iniciais = gerar_fatos(mg)
    print(len(fatos_iniciais), "fatos iniciais")
    for pred, n in contar_predicados(fatos_iniciais).most_common():
        print(f"  {pred}: {n}")

    # forward chaining até o ponto fixo
    fechamento = forward_chain(fatos_iniciais, REGRAS)

    # consultas obrigatórias >> quantos fatos de cada predicado inferido
    for pred in ["OcorrenciaSevera", "CondicaoAdversa", "PrioritariaParaAnalise"]:
        print(f"{pred}:", len(consultar_variavel(fechamento, (pred, "?o"))))

    # quais ocorrências satisfazem PrioritariaParaAnalise(?o)
    prioritarias = consultar_variavel(fechamento, ("PrioritariaParaAnalise", "?o"))
    ids = sorted(t["?o"] for t in prioritarias)
    print("Primeiros IDs prioritários:", ids[:20])


if __name__ == "__main__":
    main()
