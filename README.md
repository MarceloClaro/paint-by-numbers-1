# Pintura por Números

Aplicativo para transformar qualquer imagem em uma tela de **pintura por números**, com **paleta de cores identificada** (nome da cor, HEX, RGB, CMYK, mistura para pintura manual com Ciano/Magenta/Amarelo/Preto/Branco e porcentagem de área).

O projeto inclui:

- **Aplicativo web (Streamlit)** para uso direto no navegador.
- **CLI (linha de comando)** para gerar arquivos localmente.
- Geração de **tela numerada**, **imagem quantizada**, **paleta identificada** e **camadas separadas por cor** (PNG/SVG, compatível com corte CNC/laser).

## Funcionalidades

- Quantização de cores com **K-Means**.
- Geração de contornos e numeração das regiões.
- Identificação da paleta com:
  - Número da cor
  - Nome aproximado da cor (PT-BR)
  - Código HEX
  - Valores RGB
  - Valores CMYK (%)
  - Mistura para pintura manual: Ciano, Magenta, Amarelo, Preto e Branco (%)
  - Quantidade estimada em ml por cor e por componente (C/M/Y/P/B), conforme dimensão física e tinta total
  - Percentual de área na imagem
- Suporte a dimensões físicas da pintura em cm (até **500 x 500 cm / 5m x 5m**), formatos retangulares e quadrados.
- Recálculo automático de **altura**, **área**, **resolução (DPI/px)** e **tinta acrílica estimada (ml)** ao alterar dimensões/parâmetros.
- Exportação de resultados em PNG e paleta em CSV (no app Streamlit).
- **Camadas separadas por cor** (mapa de camadas/topográfico), com download por camada em **PNG** e **SVG vetorial** (dimensões físicas em mm para CNC/laser).

## Execução local (recomendado)

> Se o Streamlit Community Cloud estiver lento ou com limite de recursos, execute localmente para usar a CPU da sua máquina.

### Windows + WSL (atalho na Área de Trabalho)

1. Clone o repositório no WSL:
   ```bash
   git clone https://github.com/MarceloClaro/paint-by-numbers-1.git
   cd paint-by-numbers-1
   ```
2. Dê permissão ao launcher (uma vez):
   ```bash
   chmod +x iniciar_no_wsl.sh
   ```
3. Crie um atalho na Área de Trabalho do Windows (PowerShell):
   ```powershell
   $desktop = [Environment]::GetFolderPath('Desktop')
   $bat = Join-Path $desktop "Pintura por Numeros (WSL).bat"
   @"
   @echo off
   title Pintura por Numeros - WSL
   echo Iniciando Pintura por Numeros no WSL...
   wsl.exe -d Ubuntu --cd /home/marceloclaro/paint-by-numbers-1 bash -lc "./iniciar_no_wsl.sh"
   if errorlevel 1 (
     echo.
     echo Ocorreu um erro ao iniciar o app.
     pause
   )
   "@ | Set-Content -Path $bat -Encoding ASCII
   ```
4. **Dê duplo clique** em `Pintura por Numeros (WSL).bat` na Área de Trabalho.
5. Na primeira execução, o script cria `.venv-wsl`, instala dependências e inicia em `http://localhost:8501`.

Pré-requisito no WSL (Ubuntu):
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
```

### Windows (PowerShell, sem WSL)

```powershell
git clone https://github.com/MarceloClaro/paint-by-numbers-1.git
cd paint-by-numbers-1
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Linux/macOS

```bash
git clone https://github.com/MarceloClaro/paint-by-numbers-1.git
cd paint-by-numbers-1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Abra o endereço exibido pelo Streamlit (normalmente `http://localhost:8501`).

## Vídeo: como rodar localmente

Vídeo explicativo: [`docs/como-rodar-localmente.mp4`](docs/como-rodar-localmente.mp4)

## Execução local (CLI)

```bash
pip install -r requirements.txt
python run.py inputs/sua_imagem.jpg 12 --saida ./outputs --largura-cm 120 --dpi 150 --cobertura-ml-m2 150 --demoas 1
```

Exemplos:

```bash
# 12 cores, tela 120 cm de largura, altura proporcional, 150 DPI
python run.py inputs/foto.jpg 12 --saida ./outputs --largura-cm 120 --dpi 150

# 20 cores, tela retangular 120x90 cm, 2 demãos
python run.py inputs/foto.jpg 20 --largura-cm 120 --altura-cm 90 --cobertura-ml-m2 150 --demoas 2

# Usando tamanho em pixels (modo legado)
python run.py inputs/foto.jpg 16 --tamanho 4000 --saida ./outputs
```

Argumentos:

- `caminho`: caminho da imagem de entrada.
- `cores`: número de cores desejadas.
- `--plot`: `true/false` para exibir gráficos.
- `--salvar`: `true/false` para salvar arquivos.
- `--tamanho`: maior dimensão da imagem de saída em pixels (padrão: 4000).
- `--saida`: pasta de saída (padrão: `./outputs`).
- `--largura-cm`: largura física da pintura em cm (até 500).
- `--altura-cm`: altura física da pintura em cm (até 500; se omitida, calcula pela proporção).
- `--tinta-ml`: tinta total estimada em ml (se omitida e houver dimensões, calcula automaticamente pela cobertura).
- `--dpi`: resolução usada para calcular pixels a partir do tamanho físico (padrão: 150).
- `--cobertura-ml-m2`: cobertura acrílica em ml/m² por demão (padrão: 150).
- `--demoas`: número de demãos (padrão: 1).

## Deploy no Streamlit Community Cloud

O repositório está preparado para [Streamlit Community Cloud](https://share.streamlit.io/new), mas o plano gratuito pode aplicar limites de CPU/memória. Para cargas maiores, prefira execução local.

1. Faça fork/importe este repositório no GitHub.
2. Acesse [share.streamlit.io/new](https://share.streamlit.io/new).
3. Selecione o repositório e a branch.
4. Defina o arquivo principal como `streamlit_app.py`.
5. Clique em **Deploy**.

## Saídas geradas

- `*-resultado.png`: imagem quantizada (resultado esperado).
- `*-tela.png`: tela de pintura por números.
- `*-paleta.png`: paleta de cores identificada.
- `*-paleta.csv`: paleta com cores, mistura CMYKW, ml por componente e dimensões.
- `*-camada-NN.png` / `*-camada-NN.svg`: camadas separadas por cor (SVG com dimensões físicas em mm para CNC/laser).

## Estrutura

```text
.
├── canvas.py                 # Lógica de processamento e identificação da paleta
├── streamlit_app.py          # Aplicativo web Streamlit
├── run.py                    # Interface de linha de comando
├── iniciar_no_wsl.sh         # Launcher para WSL (cria venv e inicia app)
├── requirements.txt          # Dependências Python
├── packages.txt              # Pacotes de sistema (Streamlit Cloud)
├── runtime.txt               # Versão Python para Cloud
├── .python-version           # Versão Python
├── docs/                     # Vídeos/documentação
├── inputs/                   # Imagens de exemplo
└── outputs/                  # Resultados gerados
```

## Licença

Este projeto está licenciado sob a licença GPL-3.0. Veja o arquivo [LICENSE](LICENSE).
