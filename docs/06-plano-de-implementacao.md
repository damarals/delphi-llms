# Plano de Implementacao

## Fase 0 - Bootstrap

1. Criar `devcontainer` com `uv` + Ollama.
2. Definir estrutura inicial do pacote Python.
3. Configurar lint, testes basicos e CLI minima.

## Fase 1 - Dados e Contratos

1. Implementar loader do dataset.
2. Definir schemas Pydantic de entrada e saida.
3. Persistir logs JSONL por rodada e item.

## Fase 2 - Agents e Workflow

1. Implementar expert agent (prompt base + seed por expert).
2. Implementar facilitator agent (somente clarificacao).
3. Implementar workflow Agno:
   - modo padrao
   - modo recursivo
   - execucao paralela de experts

## Fase 3 - Logica Delphi

1. Agregacao por rodada.
2. Convergencia por categoria.
3. Regra de parada com `N_max=10`.
4. Fallback de maioria e desempate por mediana.

## Fase 4 - Avaliacao

1. Comparacao contra baseline humano.
2. Metricas primaria e secundarias.
3. Export para SQLite no pos-processamento.

## Fase 5 - Visualizacao

1. Painel de concordancia por item.
2. Curva de convergencia por rodada.
3. Trade-off qualidade x custo.

## Fase 6 - Verificacao

1. Rodar experimento de ponta a ponta em subset pequeno.
2. Validar reprodutibilidade minima (mesma config, mesmo resultado agregado esperado).
3. Registrar riscos e proximos ajustes antes de ampliar escala.

