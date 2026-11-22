# Roteiro — Como rodar localmente (com narração masculina)

Vídeo: [`docs/como-rodar-localmente.mp4`](./como-rodar-localmente.mp4)  
Narração: masculina, voz `pt-BR-AntonioNeural` (Microsoft Edge TTS).  
Duração aproximada: 1 min 41 s (6 cenas).

## Cena 1 — Abertura (0:00)

**Na tela**
- Pintura por Números
- Como clonar do GitHub, instalar e executar localmente
- Windows + WSL (atalho na Área de Trabalho)
- Sem limite de CPU do Streamlit Cloud

**Narração**
> Bem-vindo ao Pintura por Números. Neste vídeo, você vai ver como clonar o projeto do GitHub, instalar as dependências e executar localmente no Windows com WSL, usando um atalho na Área de Trabalho.

## Cena 2 — Pré-requisitos no WSL (0:14)

**Na tela**
- WSL Ubuntu instalado no Windows
- No terminal WSL, execute:

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
```

**Narração**
> Primeiro, você precisa do WSL com Ubuntu instalado no Windows. No terminal do Ubuntu, execute o comando para instalar o Python 3, o módulo venv e o pip.

## Cena 3 — Clonar do GitHub (0:26)

**Na tela**

```bash
git clone https://github.com/MarceloClaro/paint-by-numbers-1.git
cd paint-by-numbers-1
chmod +x iniciar_no_wsl.sh
```

**Narração**
> Depois, clone o repositório do GitHub com o comando git clone. Entre na pasta paint-by-numbers-1, e dê permissão de execução ao script iniciar_no_wsl.sh.

## Cena 4 — Criar atalho na Área de Trabalho (0:38)

**Na tela**
- Criar arquivo: `Pintura por Numeros (WSL).bat`
- Salvar na Área de Trabalho do Windows

Conteúdo do `.bat`:

```bat
@echo off
title Pintura por Numeros - WSL
echo Iniciando Pintura por Numeros no WSL...
wsl.exe -d Ubuntu --cd /home/marceloclaro/paint-by-numbers-1 bash -lc "./iniciar_no_wsl.sh"
if errorlevel 1 (
  echo.
  echo Ocorreu um erro ao iniciar o app.
  pause
)
```

**Narração**
> Agora crie um atalho na Área de Trabalho do Windows. Crie um arquivo BAT chamado Pintura por Números WSL. Dentro dele, use o comando wsl.exe para entrar na pasta do projeto no Ubuntu e executar o script iniciar_no_wsl.sh. Salve esse arquivo na sua Área de Trabalho.

## Cena 5 — Executar com duplo clique (1:00)

**Na tela**
- Dê duplo clique em `Pintura por Numeros (WSL).bat`
- Na primeira execução: cria `.venv-wsl` e instala dependências
- O app abre em `http://localhost:8501`
- Para encerrar: `Ctrl+C` ou fechar a janela

**Narração**
> Para executar, dê duplo clique no atalho. Na primeira execução, o script cria o ambiente virtual, instala as dependências e inicia o Streamlit. O aplicativo abre no navegador em localhost, porta 8501. Para encerrar, pressione Control+C ou feche a janela.

## Cena 6 — Uso no app (1:20)

**Na tela**
- Envie uma imagem, escolha cores e dimensões
- Ajuste largura: altura e ml de tinta recalculam automaticamente
- Gere tela, paleta, CSV e camadas PNG/SVG para CNC

**Narração**
> No aplicativo, envie uma imagem, escolha a quantidade de cores e as dimensões físicas. Ao alterar a largura, a altura e a estimativa de tinta em mililitros são recalculadas automaticamente. Você pode baixar a tela, a paleta, o CSV e as camadas separadas em PNG ou SVG para corte CNC.
