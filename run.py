#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI para gerar pintura por números."""

from __future__ import annotations

import argparse
import os

from canvas import Canvas


def str_para_bool(valor: str) -> bool:
    return str(valor).lower() in {"1", "true", "t", "sim", "s", "yes", "y"}


def main():
    parser = argparse.ArgumentParser(description="Gera uma tela de pintura por números a partir de uma imagem.")
    parser.add_argument("caminho", help="Caminho da imagem de entrada")
    parser.add_argument("cores", type=int, help="Número de cores (ex.: 10 a 20)")
    parser.add_argument("--plot", default="false", help="Mostrar gráficos (true/false)")
    parser.add_argument("--salvar", default="true", help="Salvar resultados (true/false)")
    parser.add_argument("--tamanho", type=int, default=4000, help="Maior dimensão da saída em pixels (padrão: 4000)")
    parser.add_argument("--saida", default="./outputs", help="Pasta de saída")
    args = parser.parse_args()

    tela = Canvas(
        os.path.abspath(args.caminho),
        args.cores,
        plot=str_para_bool(args.plot),
        save=str_para_bool(args.salvar),
        pixel_size=args.tamanho,
        output_dir=args.saida,
    )
    tela.generate()
    tela.display_colormap()
    print(f"Concluído. Arquivos salvos em: {os.path.abspath(args.saida)}")
    for cor in tela.palette_data():
        m = cor.mistura; print(f"{cor.numero:>2}. {cor.nome:<18} {cor.hex} RGB{cor.rgb} CMYK{cor.cmyk} Mistura(C,M,Y,P,B){m} Área {cor.percentual:.1f}%")


if __name__ == "__main__":
    main()
