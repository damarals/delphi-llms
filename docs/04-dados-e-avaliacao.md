# Dados e Avaliacao

## Fonte de Dados

Dataset base:
- `https://data.mendeley.com/datasets/kjzvzt8b7h`

O experimento usa os itens e resultados humanos agregados como referencia.

## Contrato de Saida por Expert

Cada resposta de expert deve respeitar JSON estrito:

1. `item_id`
2. `round`
3. `expert_id`
4. `clarification_question` (`string | null`)
5. `facilitator_answer` (`string | null`)
6. `rating` (`1..9`)
7. `category` (`enum` do dataset)
8. `rationale` (texto curto)
9. `confidence` (`0..1`)

## Artefatos de Persistencia

1. `JSONL` bruto por evento/rodada.
2. Tabelas SQLite derivadas no pos-processamento para analise.

## Metricas de Comparacao

### Primaria

1. Concordancia de decisao final por item contra humano.

### Secundarias

1. Erro absoluto de mediana por item.
2. Diferenca em `% >= 7`.
3. Diferenca em `% <= 3`.
4. Rodadas ate convergencia.
5. Custo operacional (ex.: numero de chamadas).

## Visualizacao Final (alvo)

1. Painel A: concordancia por item e por braco.
2. Painel B: curvas de convergencia por rodada (humano, padrao, recursivo).
3. Painel C: trade-off qualidade x custo.

