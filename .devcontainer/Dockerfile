FROM ghcr.io/astral-sh/uv:python3.12-bookworm

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    git \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/delphi-llms
