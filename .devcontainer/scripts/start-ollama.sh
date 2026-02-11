#!/usr/bin/env bash
set -euo pipefail

if pgrep -x "ollama" >/dev/null 2>&1; then
  exit 0
fi

nohup ollama serve >/tmp/ollama.log 2>&1 &
sleep 1

