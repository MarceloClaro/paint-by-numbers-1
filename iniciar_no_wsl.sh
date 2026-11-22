#!/usr/bin/env bash
set -euo pipefail

# Inicia o app Pintura por Números no WSL
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv-wsl"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python3 não encontrado. Instale com: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Criando ambiente virtual em $VENV_DIR..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "Instalando/atualizando dependências..."
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "Iniciando Streamlit em http://localhost:8501 ..."
echo "Pressione Ctrl+C para encerrar."

# Abre no navegador do Windows (opcional)
if command -v cmd.exe >/dev/null 2>&1; then
  (sleep 3 && cmd.exe /c start http://localhost:8501 >/dev/null 2>&1) &
fi

exec streamlit run streamlit_app.py --server.headless true --server.address 0.0.0.0 --server.port 8501
