# Pintura por Números

Aplicativo para transformar qualquer imagem em uma tela de **pintura por números**, com **paleta de cores identificada** (nome da cor, HEX, RGB, CMYK, mistura para pintura manual com Ciano/Magenta/Amarelo/Preto/Branco e porcentagem de área).

O projeto inclui:

- **Aplicativo web (Streamlit)** para uso direto no navegador.
- **CLI (linha de comando)** para gerar arquivos localmente.
- Geração de **tela numerada**, **imagem quantizada** e **paleta identificada**.

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
- Exportação de resultados em PNG e paleta em CSV (no app Streamlit).

## Deploy no Streamlit Community Cloud

Este repositório está pronto para deploy em [Streamlit Community Cloud](https://share.streamlit.io/new):

1. Faça fork/importe este repositório no GitHub.
2. Acesse [share.streamlit.io/new](https://share.streamlit.io/new).
3. Selecione o repositório e a branch.
4. Defina o arquivo principal como `streamlit_app.py`.
5. Clique em **Deploy**.

## Execução local (Streamlit)

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Execução local (CLI)

```bash
pip install -r requirements.txt
python run.py caminho/da/imagem.jpg 12 --saida ./outputs --largura-cm 120 --dpi 150 --cobertura-ml-m2 150 --demoas 1
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

## Saídas geradas

- `*-resultado.png`: imagem quantizada (resultado esperado).
- `*-tela.png`: tela de pintura por números.
- `*-paleta.png`: paleta de cores identificada.

## Estrutura

```text
.
├── canvas.py              # Lógica de processamento e identificação da paleta
├── streamlit_app.py       # Aplicativo web Streamlit
├── run.py                 # Interface de linha de comando
├── requirements.txt       # Dependências Python
├── packages.txt           # Pacotes de sistema (Streamlit Cloud)
├── inputs/                # Imagens de exemplo
└── outputs/               # Resultados gerados
```

## Licença

Este projeto está licenciado sob a licença GPL-3.0. Veja o arquivo [LICENSE](LICENSE).
