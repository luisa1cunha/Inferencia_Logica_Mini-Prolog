"""Motor lógico >> substituição, unificação, casamento de premissas e forward chaining

Este módulo só sabe unificar e encadear regras
As conclusões sobre as ocorrências surgem apenas das regras definidas em regras.py

Convenções >>
- Fato/átomo: tupla, ("Chuva", 123456)
    >> o primeiro elemento é o predicado, os demais são os argumentos.
- Variável: string que começa com "?", ex "?o"
- Regra: par (lista_de_premissas, conclusao)
    ex ([("Chuva", "?o"), ("Curva", "?o")], ("CondicaoAdversa", "?o"))
- theta: dicionário de substituição, ex {"?o": 123456}
    >> guarda qual valor cada variável assumiu até agora
- Predicado embutido: ("Diferente", a, b), verificado pelo próprio motor
"""
from collections import defaultdict


def eh_var(x):
    #True se x é uma variável (string começando com '?')
    return isinstance(x, str) and x.startswith("?")


def tem_variavel(expr):
    #True se a expressão ainda contém alguma variável livre
    if eh_var(expr):
        return True
    if isinstance(expr, tuple):
        # Basta uma variável em qualquer posição da tupla
        return any(tem_variavel(e) for e in expr)
    return False


def substituir(expr, theta):
    """Troca as variáveis de `expr` pelos valores que estão em `theta`

    Exemplo >>
        substituir(("Chuva", "?o"), {"?o": 123456}) -> ("Chuva", 123456)

    Variáveis que não estão em theta permanecem como estão
    """
    if eh_var(expr):
        # Segue cadeias: se ?a -> ?b e ?b -> 5, então ?a vira 5
        while eh_var(expr) and expr in theta:
            expr = theta[expr]
        return expr
    if isinstance(expr, tuple):
        # Aplica a substituição em cada elemento do átomo (recursivo).
        return tuple(substituir(e, theta) for e in expr)
    # Constantes (números, nomes de predicado) ficam iguais.
    return expr


def unificar(a, b, theta=None):
    """Tenta tornar `a` e `b` iguais, descobrindo os valores das variáveis

    Devolve o theta estendido se conseguir, ou None se falhar

    Exemplos >>
        unificar(("Chuva", "?o"), ("Chuva", 1))   -> {"?o": 1}
        unificar(("Chuva", "?o"), ("Curva", 1))   -> None (predicados diferentes)
        unificar(("Chuva", "?o"), ("Chuva", 999), {"?o": 1}) -> None
            (?o já valia 1, não pode valer 999 também)

    O último caso é o que garante que duas premissas de uma regra
    falem da MESMA ocorrência 
    """
    if theta is None:
        theta = {}

    # Aplica o que já se sabe antes de comparar
    a = substituir(a, theta)
    b = substituir(b, theta)

    if a == b:
        return theta                      # já são iguais: nada a acrescentar
    if eh_var(a):
        return {**theta, a: b}            # liga a variável de a ao valor de b
    if eh_var(b):
        return {**theta, b: a}            # liga a variável de b ao valor de a
    if isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b):
        # Dois átomos do mesmo tamanho >> unifica elemento por elemento,
        # carregando o theta de um para o próximo
        for x, y in zip(a, b):
            theta = unificar(x, y, theta)
            if theta is None:
                return None               # um elemento falhou: tudo falha
        return theta
    return None                           # constantes diferentes ou tamanhos diferentes


def indexar(fatos):
    """Agrupa os fatos por predicado: {predicado: {fatos}}
    ao buscar fatos para uma premissa Chuva(?o), o motor olha
    só o grupo "Chuva" em vez de varrer todos os fatos da base
    """
    indice = defaultdict(set)
    for f in fatos:
        indice[f[0]].add(f)               # f[0] é o nome do predicado
    return indice


def casar_premissas(premissas, fatos, theta=None, indice=0):
    """Gera todos os thetas que satisfazem as premissas a partir de `indice`

    É um gerador recursivo, usa yield >>
    - pega a premissa atual e tenta unificá-la com cada fato do mesmo predicado
    - para cada sucesso, chama a si mesma para a proxima premissa,
      carregando o theta já atualizado;
    - quando passa da última premissa, todas foram satisfeitas: devolve theta

    `fatos` pode ser um set de fatos ou um índice (dict predicado -> fatos)
    """
    if theta is None:
        theta = {}
    if not isinstance(fatos, dict):
        fatos = indexar(fatos)

    # Caso base >> todas as premissas foram casadas, theta é uma solução
    if indice == len(premissas):
        yield theta
        return

    # Aplica o que já foi descoberto (ex.: ?o já vale 123456) à premissa atual.=
    premissa = substituir(premissas[indice], theta)

    # Predicado embutido>> Diferente(a, b) é verdadeiro se a != b
    # Só pode ser avaliado quando ambos já têm valor (sem variáveis)
    if premissa[0] == "Diferente":
        if not tem_variavel(premissa) and premissa[1] != premissa[2]:
            yield from casar_premissas(premissas, fatos, theta, indice + 1)
        return

    # Premissa já totalmente instanciada, não há o que descobrir, só checar se o fato existe
    if not tem_variavel(premissa):
        if premissa in fatos.get(premissa[0], ()):
            yield from casar_premissas(premissas, fatos, theta, indice + 1)
        return

    # Premissa com variáveis: tenta unificar com cada fato do mesmo predicado.
    for fato in fatos.get(premissa[0], ()):
        novo_theta = unificar(premissa, fato, theta)
        if novo_theta is not None:
            # Deu certo para esta premissa: segue para a próxima.
            yield from casar_premissas(premissas, fatos, novo_theta, indice + 1)


def forward_chain(fatos_iniciais, regras, verbose=True):
    """Aplica as regras repetidamente até o ponto fixo e devolve a base fechada

    Ponto fixo>> uma rodada completa que não gera nenhum fato novo

    Cada rodada:
      1. para cada regra, acha todos os thetas que satisfazem as premissas
      2. instancia a conclusão com cada theta
      3. guarda as conclusões que ainda não estavam na base
    Os fatos novos só entram na base depois de todas as regras da rodada
    terem rodado. Por isso o encadeamento aparece em rodadas distintas:
      rodada 1: R1 a R4 (Severa, CondicaoAdversa)
      rodada 2: R5 e R6 (Prioritaria), que dependem dos fatos da rodada 1
    """
    fatos = set(fatos_iniciais)           # cópia>> não altera o conjunto original
    indice = indexar(fatos)
    rodada = 0

    while True:
        novos = set()
        for premissas, conclusao in regras:
            for theta in casar_premissas(premissas, indice):
                novo = substituir(conclusao, theta)
                if novo not in fatos:     # só interessa o que é realmente novo
                    novos.add(novo)

        if not novos:                     # nada de novo>> ponto fixo atingido
            if verbose:
                print(f"Ponto fixo atingido após {rodada} rodada(s) com fatos novos.")
            break

        rodada += 1
        if verbose:
            print(f"Rodada {rodada}: {len(novos)} fatos novos")

        # Incorpora os fatos novos na base e no índice para a próxima rodada
        fatos |= novos
        for f in novos:
            indice[f[0]].add(f)

    return fatos


def consulta(fatos, pergunta):
    """Pergunta sem variáveis >> o fato está na base? devolve True/False

    Exemplo>> consulta(fechamento, ("PrioritariaParaAnalise", 123456))
    """
    return pergunta in fatos


def consultar_variavel(fatos, query):
    """Pergunta comvariáveis >> devolve todos os thetas que a satisfazem

    Exemplo>> consultar_variavel(fechamento, ("PrioritariaParaAnalise", "?o"))
        -> [{"?o": 111}, {"?o": 222}, ...]  (um theta por ocorrência)
    """
    if not isinstance(fatos, dict):
        fatos = indexar(fatos)
    resultados = []
    # Só os fatos do mesmo predicado da pergunta podem unificar
    for fato in fatos.get(query[0], ()):
        theta = unificar(query, fato)
        if theta is not None:
            resultados.append(theta)
    return resultados
