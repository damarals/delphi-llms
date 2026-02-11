# Contexto e Objetivo

## Problema Atual

O foco atual nao e paper nem automacao completa de SLR.  
O foco e validar, por POC, se um processo Delphi com LLMs consegue se alinhar ao julgamento humano em um protocolo controlado.

Dataset de referencia:
- Mendeley Data: `kjzvzt8b7h` (Delphi com especialistas humanos)
- Link: `https://data.mendeley.com/datasets/kjzvzt8b7h`

## Objetivo da POC

Comparar resultados de Delphi com LLMs contra baseline humano do dataset, preservando as categorias originais e medindo:

1. Decisao final por item (prioridade principal).
2. Metricas agregadas por item (apoio/explicabilidade).

## O que esta fora de escopo agora

1. Escrita de paper.
2. Generalizacao para pipeline completo de SLR automatizada.
3. Integracoes de producao.

## Definicao de Sucesso (POC)

1. Rodar os 3 bracos experimentais com protocolo reprodutivel.
2. Gerar comparacao objetiva contra baseline humano.
3. Produzir visualizacoes que mostrem alinhamento, convergencia e custo-beneficio.

