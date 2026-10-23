from src.motor_logico import (
    casar_premissas, consulta, consultar_variavel,
    forward_chain, substituir, unificar,
)
from src.regras import REGRAS


def test_substituir():
    assert substituir(("Chuva", "?o"), {"?o": 1}) == ("Chuva", 1)


def test_unificar_sucesso_e_falha():
    assert unificar(("Chuva", "?o"), ("Chuva", 1)) == {"?o": 1}
    assert unificar(("Chuva", "?o"), ("Curva", 1)) is None
    assert unificar(("Chuva", "?o"), ("Chuva", 999), {"?o": 1}) is None


def test_casar_premissas_exige_mesma_ocorrencia():
    fatos = {("Chuva", 1), ("Curva", 2)}
    premissas = [("Chuva", "?o"), ("Curva", "?o")]
    assert list(casar_premissas(premissas, fatos)) == []


def test_diferente():
    fatos = {("P", 1), ("P", 2)}
    premissas = [("P", "?a"), ("P", "?b"), ("Diferente", "?a", "?b")]
    pares = {(t["?a"], t["?b"]) for t in casar_premissas(premissas, fatos)}
    assert pares == {(1, 2), (2, 1)}


def test_forward_chain_exemplo_pequeno():
    fatos = {
        ("TemFeridoGrave", 1), ("Chuva", 1), ("Curva", 1),
        ("TemVitimaFatal", 2), ("ColisaoFrontal", 2),
        ("TemVitimaFatal", 3),
        ("Chuva", 4), ("Curva", 4),
    }
    res = forward_chain(fatos, REGRAS, verbose=False)
    ids = {t["?o"] for t in consultar_variavel(res, ("PrioritariaParaAnalise", "?o"))}
    assert ids == {1, 2}
    assert consulta(res, ("OcorrenciaSevera", 3))
    assert not consulta(res, ("PrioritariaParaAnalise", 3))
    assert consulta(res, ("CondicaoAdversa", 4))
