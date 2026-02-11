# Ambiente Devcontainer

## Objetivo

Garantir ambiente reproduzivel para desenvolver e executar experimento local com:

1. Python + `uv`
2. Agno
3. Ollama em servico dedicado (`ollama/ollama`) via Docker Compose do devcontainer
4. GPU opcional com fallback CPU

## Decisoes Fechadas

1. Base de imagem orientada a `uv` (conforme guia oficial).
2. Ollama via container oficial (sem install script no app container).
3. Execucao deve funcionar sem GPU; usar GPU quando disponivel.

Referencia:
- `https://docs.astral.sh/uv/guides/integration/docker/`
- `https://docs.ollama.com/docker`

## Requisitos de Configuracao

1. Versoes de Python e dependencias fixadas.
2. Arquivo de lock do `uv` versionado.
3. Variaveis de ambiente documentadas:
   - `OLLAMA_HOST`
   - parametros de modelo e runtime
4. Scripts de bootstrap para:
   - baixar modelo (`Qwen3-4B`)
   - validar saude do ambiente

## Criterios de Pronto

1. `devcontainer up` sem erros.
2. Comando de sanity check para Ollama responde.
3. Pipeline Python executa comando de teste inicial.
