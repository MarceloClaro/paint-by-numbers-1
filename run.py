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
    parser.add_argument("--largura-cm", type=float, default=None, help="Largura física da pintura em cm (até 500)")
    parser.add_argument("--altura-cm", type=float, default=None, help="Altura física da pintura em cm (até 500)")
    parser.add_argument("--tinta-ml", type=float, default=None, help="Tinta total estimada em ml")
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
    largura_cm = args.largura_cm
    altura_cm = args.altura_cm
    if largura_cm and not altura_cm and tela.quantified_image is not None:
        h, w = tela.quantified_image.shape[:2]
        altura_cm = largura_cm * h / max(1, w)
    if altura_cm and not largura_cm and tela.quantified_image is not None:
        h, w = tela.quantified_image.shape[:2]
        largura_cm = altura_cm * w / max(1, h)
    tela.display_colormap(total_ml=args.tinta_ml, largura_cm=largura_cm, altura_cm=altura_cm)
    print(f"Concluído. Arquivos salvos em: {os.path.abspath(args.saida)}")
    if largura_cm and altura_cm:
        print(f"Dimensão física: {largura_cm:.1f} x {altura_cm:.1f} cm | Área: {largura_cm*altura_cm:.0f} cm²")
    if args.tinta_ml:
        print(f"Tinta total estimada: {args.tinta_ml:.1f} ml")
    for cor in tela.palette_data():
        m = cor.mistura
        ml_cor = (float(args.tinta_ml) * cor.percentual / 100.0) if args.tinta_ml else None
        ml_txt = ""
        if ml_cor is not None:
            ml_parts = [ml_cor * x / 100.0 for x in m]
            ml_txt = f" Tinta {ml_cor:.2f}ml [C:{ml_parts[0]:.2f} M:{ml_parts[1]:.2f} Y:{ml_parts[2]:.2f} P:{ml_parts[3]:.2f} B:{ml_parts[4]:.2f}]"
        print(f"{cor.numero:>2}. {cor.nome:<18} {cor.hex} RGB{cor.rgb} CMYK{cor.cmyk} Mistura(C,M,Y,P,B){m}{ml_txt} Área {cor.percentual:.1f}%")


if __name__ == "__main__":
    main()
