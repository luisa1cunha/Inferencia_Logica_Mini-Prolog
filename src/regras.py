"""Regras de inferência didáticas

Cada regra é um par (premissas, conclusao) >>
A regra vale quando TODAS as premissas são verdadeiras para o mesmo valor de "?o"

Encadeamento >>
    fatos do CSV --R1/R2--> OcorrenciaSevera  --\
    fatos do CSV --R3/R4--> CondicaoAdversa   ---+--R5/R6--> PrioritariaParaAnalise
"""

# R1: TemVitimaFatal(o) -> OcorrenciaSevera(o)
R1 = ([("TemVitimaFatal", "?o")], ("OcorrenciaSevera", "?o"))

# R2: TemFeridoGrave(o) -> OcorrenciaSevera(o)
R2 = ([("TemFeridoGrave", "?o")], ("OcorrenciaSevera", "?o"))

# R3: Chuva(o) E Curva(o) -> CondicaoAdversa(o)
R3 = ([("Chuva", "?o"), ("Curva", "?o")], ("CondicaoAdversa", "?o"))

# R4: PlenaNoite(o) E PistaSimples(o) -> CondicaoAdversa(o)
R4 = ([("PlenaNoite", "?o"), ("PistaSimples", "?o")], ("CondicaoAdversa", "?o"))

# R5: OcorrenciaSevera(o) E CondicaoAdversa(o) -> PrioritariaParaAnalise(o)
#     (depende de fatos inferidos por R1/R2 e R3/R4)
R5 = ([("OcorrenciaSevera", "?o"), ("CondicaoAdversa", "?o")],
      ("PrioritariaParaAnalise", "?o"))

# R6: OcorrenciaSevera(o) E ColisaoFrontal(o) -> PrioritariaParaAnalise(o)
R6 = ([("OcorrenciaSevera", "?o"), ("ColisaoFrontal", "?o")],
      ("PrioritariaParaAnalise", "?o"))

# Lista usada pelo forward_chain. A ordem não altera o resultado final.
REGRAS = [R1, R2, R3, R4, R5, R6]
