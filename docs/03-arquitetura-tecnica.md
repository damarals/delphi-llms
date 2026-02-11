# Arquitetura Tecnica

## Stack

1. Linguagem: Python.
2. Orquestracao: Agno (workflow, loop, parallel, early stop).
3. Inferencia local: Ollama.
4. Modelo base inicial: `Qwen3-4B`.
5. Persistencia:
   - Runtime bruto: JSONL.
   - Pos-processamento: SQLite (sem escrita concorrente em tempo real).

## Filosofia de Implementacao

Agno sera usado para orquestracao de estados e fluxo.  
A logica metodologica critica ficara em codigo proprio:

1. schema/validacao de resposta
2. agregacao de rodada
3. criterio de parada e fallback
4. comparacao com baseline
5. metricas e visualizacoes

## Estrutura de Modulos (alvo)

```text
src/delphi_llms/
  config.py
  models.py
  data/
    loader.py
    schema.py
  agents/
    expert.py
    facilitator.py
  delphi/
    engine.py
    stopping.py
    aggregation.py
  eval/
    metrics.py
    compare.py
  viz/
    plots.py
  cli.py
```

## Fluxo de Execucao

1. Carrega e normaliza itens e baseline humano.
2. Inicializa painel de 5 experts (mesmo prompt base, seeds diferentes).
3. Executa rodada em paralelo.
4. No recursivo, cada expert faz 1 clarificacao antes do rating.
5. Agrega resultados.
6. Verifica convergencia ou `N_max`.
7. Decide resultado final por item.
8. Compara com baseline humano.
9. Gera artefatos de avaliacao e visualizacao.

