# Desenho Experimental

## Bracos

1. `Humano (baseline Mendeley)`
2. `LLM Delphi Padrao`
   - Entrada: item
   - Saida: `rating + category + rationale`
3. `LLM Delphi Recursivo`
   - Entrada: item
   - Passo extra: 1 pergunta de clarificacao ao facilitador
   - Saida: `rating + category + rationale`

## Regras Comuns

1. Mesmas categorias originais do dataset (sem simplificacao).
2. Mesmo modelo base de expert no padrao e recursivo.
3. Painel com `5 experts`.
4. Experts executados em paralelo por rodada.
5. Saida estruturada em JSON estrito por expert.

## Facilitador (apenas no recursivo)

1. Papel: somente clarificacao.
2. Pode recusar perguntas fora do escopo.
3. Nao sugere nota nem decisao final.
4. Nao usa rotulo alvo (sem leakage do gabarito).
5. `N_clarif = 1` interacao por item por rodada.

## Rodadas e Parada

1. O processo roda por criterio de parada (nao fixo em 2).
2. Criterio principal: convergencia total por categoria na rodada atual.
   - Todos os 5 experts com a mesma categoria final.
3. Fallback de seguranca: `N_max = 10` rodadas.
4. Se atingir `N_max` sem convergencia:
   - decisao por maioria de votos;
   - desempate por mediana.

## Comparabilidade com Mendeley

1. Analise principal pode usar corte em 2 rodadas para comparacao direta.
2. Analise estendida usa loop ate convergencia ou `N_max`.

