FROM ghcr.io/astral-sh/uv:python3.12-bookworm

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Install Ollama inside the container.
RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /workspaces/delphi-llms

