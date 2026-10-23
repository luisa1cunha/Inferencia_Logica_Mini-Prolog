# Inferência Lógica sobre Acidentes em Rodovias Federais

Exercício prático de **Inteligência Artificial (SIN 323, UFV)**: lógica de primeira ordem,
unificação e *forward chaining* aplicados a dados reais de acidentes da PRF (2025, Minas Gerais)

> As regras são critérios **didáticos** definidos para a disciplina. Não representam critérios oficiais de priorização da PRF

## Como funciona

1. Cada ocorrência do CSV vira **fatos** (ex.: `Chuva(123456)`).
2. Um motor lógico próprio (sem bibliotecas de lógica/Prolog) aplica as **regras** R1 a R6
   repetidamente até o **ponto fixo**.
3. Consultas na base final respondem quantas ocorrências são `OcorrenciaSevera`,
   `CondicaoAdversa` e `PrioritariaParaAnalise`.

O Pandas é usado apenas para leitura, filtragem e preparação do CSV.

## Como executar
1. No Google Colab, adicione o zip do projeto e execute o codigo >>
    !unzip -o prf-inferencia-logica.zip
    %cd prf-inferencia-logica

2. Baixe o CSV **Acidentes 2025 (Agrupados por ocorrência)** em
   [Dados Abertos da PRF](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf)
   e salve em `data/datatran2025.csv`

3. Use para executar o código completo >>
   !pip install -q -r requirements.txt
   !python main.py --csv data/datatran2025.csv
