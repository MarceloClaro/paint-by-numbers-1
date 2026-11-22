#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geração de tela de pintura por números a partir de uma imagem."""

from __future__ import annotations

import os

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.utils import shuffle


# Paleta de referência para identificação por nome (PT-BR).
CORES_REFERENCIA: list[tuple[str, tuple[int, int, int]]] = [
    ("Preto", (0, 0, 0)),
    ("Branco", (255, 255, 255)),
    ("Cinza Escuro", (64, 64, 64)),
    ("Cinza", (128, 128, 128)),
    ("Cinza Claro", (192, 192, 192)),
    ("Cinza Quente", (112, 102, 96)),
    ("Vermelho", (220, 20, 60)),
    ("Vermelho Escuro", (139, 0, 0)),
    ("Vermelho Tijolo", (178, 34, 34)),
    ("Bordô", (128, 0, 32)),
    ("Rosa", (255, 105, 180)),
    ("Rosa Claro", (255, 182, 193)),
    ("Rosa Antigo", (188, 143, 143)),
    ("Salmão", (250, 128, 114)),
    ("Coral", (255, 127, 80)),
    ("Laranja", (255, 140, 0)),
    ("Laranja Escuro", (255, 69, 0)),
    ("Pêssego", (255, 218, 185)),
    ("Amarelo", (255, 215, 0)),
    ("Amarelo Claro", (255, 255, 153)),
    ("Amarelo Mostarda", (204, 153, 0)),
    ("Ocre", (204, 119, 34)),
    ("Bege", (245, 245, 220)),
    ("Areia", (194, 178, 128)),
    ("Creme", (255, 253, 208)),
    ("Marrom", (139, 69, 19)),
    ("Marrom Escuro", (101, 67, 33)),
    ("Marrom Claro", (205, 133, 63)),
    ("Marrom Avermelhado", (150, 75, 0)),
    ("Terracota", (180, 90, 60)),
    ("Caramelo", (175, 110, 60)),
    ("Verde", (34, 139, 34)),
    ("Verde Escuro", (0, 100, 0)),
    ("Verde Claro", (144, 238, 144)),
    ("Verde Oliva", (128, 128, 0)),
    ("Verde Musgo", (85, 107, 47)),
    ("Verde Sálvia", (120, 140, 100)),
    ("Verde Floresta", (34, 85, 34)),
    ("Verde Água", (64, 224, 208)),
    ("Turquesa", (0, 206, 209)),
    ("Ciano", (0, 255, 255)),
    ("Azul", (30, 144, 255)),
    ("Azul Escuro", (0, 0, 139)),
    ("Azul Marinho", (25, 25, 112)),
    ("Azul Claro", (173, 216, 230)),
    ("Azul Acinzentado", (112, 128, 144)),
    ("Azul Petróleo", (0, 95, 106)),
    ("Roxo", (128, 0, 128)),
    ("Violeta", (138, 43, 226)),
    ("Lilás", (200, 162, 200)),
    ("Magenta", (255, 0, 255)),
    ("Índigo", (75, 0, 130)),
    ("Dourado", (212, 175, 55)),
    ("Prata", (176, 176, 176)),
    ("Bronze", (205, 127, 50)),
    ("Pele Clara", (255, 224, 196)),
    ("Pele Média", (210, 160, 120)),
    ("Pele Escura", (140, 90, 60)),
]


class CorIdentificada:
    """Informações identificadas de uma cor da paleta."""

    __slots__ = ("numero", "nome", "rgb", "hex", "cmyk", "mistura", "percentual")

    def __init__(self, numero: int, nome: str, rgb: tuple[int, int, int], hex: str,
                 cmyk: tuple[float, float, float, float],
                 mistura: tuple[float, float, float, float, float],
                 percentual: float):
        self.numero = numero
        self.nome = nome
        self.rgb = rgb
        self.hex = hex
        self.cmyk = cmyk
        self.mistura = mistura
        self.percentual = percentual

    def __repr__(self):
        return (f"CorIdentificada(numero={self.numero!r}, nome={self.nome!r}, rgb={self.rgb!r}, "
                f"hex={self.hex!r}, cmyk={self.cmyk!r}, mistura={self.mistura!r}, percentual={self.percentual!r})")

    def __eq__(self, other):
        if not isinstance(other, CorIdentificada):
            return NotImplemented
        return self.__dict__ if False else (
            self.numero, self.nome, self.rgb, self.hex, self.cmyk, self.mistura, self.percentual
        ) == (other.numero, other.nome, other.rgb, other.hex, other.cmyk, other.mistura, other.percentual)


def rgb_para_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def rgb_para_cmyk(rgb: tuple[int, int, int]) -> tuple[float, float, float, float]:
    r, g, b = [c / 255.0 for c in rgb]
    k = 1 - max(r, g, b)
    if k >= 1.0 - 1e-9:
        return 0.0, 0.0, 0.0, 100.0
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return round(c * 100, 1), round(m * 100, 1), round(y * 100, 1), round(k * 100, 1)


def rgb_para_mistura_pintura(rgb: tuple[int, int, int]) -> tuple[float, float, float, float, float]:
    """Mistura heurística para pintura manual: Ciano, Magenta, Amarelo, Preto, Branco (%)."""
    r, g, b = [max(0.0, min(1.0, c / 255.0)) for c in rgb]
    branco = min(r, g, b)
    # Remove componente branco e calcula CMYK no restante
    c, m, y, k = rgb_para_cmyk(rgb)
    # Distribui: branco ocupa branco*100 do total; restante proporcional ao CMYK
    branco_pct = branco * 100.0
    restante = 100.0 - branco_pct
    soma = c + m + y + k
    if soma <= 1e-9:
        return 0.0, 0.0, 0.0, 0.0, 100.0
    c_pct = restante * c / soma
    m_pct = restante * m / soma
    y_pct = restante * y / soma
    k_pct = restante * k / soma
    vals = [c_pct, m_pct, y_pct, k_pct, branco_pct]
    # normaliza para somar 100
    total = sum(vals)
    if total > 1e-9:
        vals = [v * 100.0 / total for v in vals]
    return tuple(round(v, 1) for v in vals)  # type: ignore


def nome_cor_proxima(rgb: tuple[int, int, int]) -> str:
    melhor_nome = "Cor personalizada"
    melhor_dist = float("inf")
    r, g, b = rgb
    for nome, (rr, gg, bb) in CORES_REFERENCIA:
        dist = (r - rr) ** 2 + (g - gg) ** 2 + (b - bb) ** 2
        if dist < melhor_dist:
            melhor_dist = dist
            melhor_nome = nome
    return melhor_nome


class Canvas:
    """Cria uma tela de pintura por números a partir de uma imagem."""

    def __init__(
        self,
        origem,
        nb_color: int,
        plot: bool = False,
        save: bool = True,
        pixel_size: int = 4000,
        output_dir: str = "./outputs",
    ):
        if isinstance(origem, str):
            self.path = origem
            self.namefile = os.path.splitext(os.path.basename(origem))[0]
            img = cv2.imread(origem)
            if img is None:
                raise FileNotFoundError(f"Não foi possível ler a imagem: {origem}")
            self.src = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            self.path = None
            self.namefile = "imagem"
            self.src = np.asarray(origem)
            if self.src.ndim == 2:
                self.src = cv2.cvtColor(self.src, cv2.COLOR_GRAY2RGB)
            elif self.src.shape[2] == 4:
                self.src = cv2.cvtColor(self.src, cv2.COLOR_RGBA2RGB)

        self.nb_color = max(1, int(nb_color))
        self.plot = bool(plot)
        self.save = bool(save)
        self.tar_width = max(100, int(pixel_size))
        self.output_dir = output_dir
        self.colormap: list[tuple[int, int, int]] = []
        self.palette: list[CorIdentificada] = []
        self.quantified_image: np.ndarray | None = None
        self.canvas: np.ndarray | None = None

    def generate(self):
        im_source = self.resize()
        clean_img = self.cleaning(im_source)
        clean_img = np.array(clean_img, dtype="uint8") / 255.0
        quantified_image, colors = self.quantification(clean_img)
        canvas = np.ones(quantified_image.shape[:2], dtype="uint8") * 255

        q8 = np.clip(np.rint(quantified_image * 255), 0, 255).astype(np.uint8)
        total_pixels = q8.shape[0] * q8.shape[1]
        self.colormap = []
        self.palette = []

        for ind, color in enumerate(colors):
            rgb = tuple(int(round(c * 255)) for c in color)
            rgb = tuple(min(255, max(0, v)) for v in rgb)
            self.colormap.append(rgb)

            mask = cv2.inRange(q8, np.array(rgb, dtype=np.uint8), np.array(rgb, dtype=np.uint8))
            percentual = float(np.count_nonzero(mask)) / float(total_pixels) * 100.0
            self.palette.append(
                CorIdentificada(
                    numero=ind + 1,
                    nome=nome_cor_proxima(rgb),
                    rgb=rgb,
                    hex=rgb_para_hex(rgb),
                    cmyk=rgb_para_cmyk(rgb),
                    mistura=rgb_para_mistura_pintura(rgb),
                    percentual=round(percentual, 2),
                )
            )

            cnts = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]

            for contour in cnts:
                area = abs(cv2.contourArea(contour))
                _, _, width_ctr, height_ctr = cv2.boundingRect(contour)
                if width_ctr < 10 or height_ctr < 10 or area < 100:
                    continue
                cv2.drawContours(canvas, [contour], -1, (0, 0, 0), 1)
                tx, ty = self._posicao_rotulo(contour)
                cv2.putText(
                    canvas,
                    str(ind + 1),
                    (tx, ty),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (0, 0, 0),
                    1,
                    cv2.LINE_AA,
                )

        self.quantified_image = q8
        self.canvas = canvas

        if self.plot:
            self.plot_figure(self.quantified_image, "Resultado esperado")
            self.plot_figure(canvas, "Tela para pintar")

        if self.save:
            self._ensure_output_dir()
            cv2.imwrite(
                os.path.join(self.output_dir, f"{self.namefile}-resultado.png"),
                cv2.cvtColor(self.quantified_image, cv2.COLOR_RGB2BGR),
            )
            cv2.imwrite(os.path.join(self.output_dir, f"{self.namefile}-tela.png"), canvas)

        return canvas

    def _ensure_output_dir(self):
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def _posicao_rotulo(contour):
        m = cv2.moments(contour)
        if abs(m.get("m00", 0.0)) > 1e-5:
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])
            return cx - 5, cy + 5
        x, y = contour[0][0]
        return int(x), int(y + 10)

    def resize(self):
        (height, width) = self.src.shape[:2]
        if height > width:
            dim = (int(width * self.tar_width / float(height)), self.tar_width)
        else:
            dim = (self.tar_width, int(height * self.tar_width / float(width)))
        return cv2.resize(self.src, dim, interpolation=cv2.INTER_AREA)

    def cleaning(self, picture):
        clean_pic = cv2.fastNlMeansDenoisingColored(picture, None, 10, 10, 7, 21)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
        clean_pic = cv2.morphologyEx(clean_pic, cv2.MORPH_OPEN, kernel, cv2.BORDER_REPLICATE)
        clean_pic = cv2.morphologyEx(clean_pic, cv2.MORPH_CLOSE, kernel, cv2.BORDER_REPLICATE)
        return clean_pic

    def quantification(self, picture):
        width, height, dimension = tuple(picture.shape)
        image_array = np.reshape(picture, (width * height, dimension))
        sample_size = min(1000, len(image_array))
        image_array_sample = shuffle(image_array, random_state=0, n_samples=sample_size)
        kmeans = KMeans(n_clusters=self.nb_color, random_state=42, n_init=10).fit(image_array_sample)
        labels = kmeans.predict(image_array)
        new_img = self.recreate_image(kmeans.cluster_centers_, labels, width, height)
        return new_img, kmeans.cluster_centers_

    @staticmethod
    def recreate_image(codebook, labels, width, height):
        return codebook[labels].reshape(width, height, -1)

    def palette_data(self):
        if not self.palette and self.colormap:
            for i, rgb in enumerate(self.colormap):
                self.palette.append(
                    CorIdentificada(
                        numero=i + 1,
                        nome=nome_cor_proxima(rgb),
                        rgb=rgb,
                        hex=rgb_para_hex(rgb),
                        cmyk=rgb_para_cmyk(rgb),
                        mistura=rgb_para_mistura_pintura(rgb),
                        percentual=0.0,
                    )
                )
        return self.palette

    def display_colormap(self, total_ml: float | None = None, largura_cm: float | None = None, altura_cm: float | None = None, dpi: int | None = None):
        palette = self.palette_data()
        if not palette:
            return None

        show_ml = total_ml is not None and float(total_ml) > 0
        row_h = 32
        header_h = 86 if show_ml else 70
        margin = 20

        # Definição de colunas: (titulo, x, largura_aprox)
        cols = [
            ("Nº", 20),
            ("Cor", 55),
            ("Nome", 110),
            ("HEX", 290),
            ("RGB", 380),
            ("CMYK(C,M,Y,K)%", 520),
            ("C", 700),
            ("M", 740),
            ("Y", 780),
            ("P", 820),
            ("B", 860),
        ]
        if show_ml:
            cols += [
                ("mlCor", 910),
                ("mlC", 970),
                ("mlM", 1025),
                ("mlY", 1080),
                ("mlP", 1135),
                ("mlB", 1190),
                ("Área%", 1255),
            ]
            width = 1340
        else:
            cols += [("Área%", 920)]
            width = 1010

        height = header_h + len(palette) * row_h + 20
        picture = np.ones((height, width, 3), dtype="uint8") * 255

        titulo = "Paleta de Cores Identificada - Mistura para Pintura Manual"
        cv2.putText(picture, titulo, (margin, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (0, 0, 0), 2, cv2.LINE_AA)

        dim_txt = ""
        if largura_cm and altura_cm:
            dim_txt = f"Dimensão: {float(largura_cm):.1f} x {float(altura_cm):.1f} cm"
        if show_ml:
            dim_txt += (" | " if dim_txt else "") + f"Tinta total: {float(total_ml):.1f} ml"
        if dpi and largura_cm and altura_cm:
            wpx = round(float(largura_cm) / 2.54 * int(dpi))
            hpx = round(float(altura_cm) / 2.54 * int(dpi))
            dim_txt += (" | " if dim_txt else "") + f"{int(dpi)} DPI ({wpx}x{hpx}px)"
        if dim_txt:
            cv2.putText(picture, dim_txt, (margin, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (60, 60, 60), 1, cv2.LINE_AA)

        # Cabeçalho das colunas
        y_head = 68
        for col_name, x in cols:
            cv2.putText(picture, col_name, (x, y_head), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (40, 40, 40), 1, cv2.LINE_AA)
        cv2.line(picture, (margin, y_head + 8), (width - margin, y_head + 8), (180, 180, 180), 1)
        cv2.putText(picture, "Mistura pintura manual: C=Ciano, M=Magenta, Y=Amarelo, P=Preto, B=Branco (%)", (margin, y_head + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (90, 90, 90), 1, cv2.LINE_AA)

        for i, cor in enumerate(palette):
            y = header_h + 18 + i * row_h
            if i % 2 == 0:
                cv2.rectangle(picture, (margin - 5, y - 18), (width - margin, y + 10), (245, 245, 245), -1)

            values = {
                "Nº": f"{cor.numero}",
                "Cor": None,  # swatch
                "Nome": cor.nome[:20],
                "HEX": cor.hex,
                "RGB": f"{cor.rgb[0]},{cor.rgb[1]},{cor.rgb[2]}",
                "CMYK(C,M,Y,K)%": f"{cor.cmyk[0]:.0f},{cor.cmyk[1]:.0f},{cor.cmyk[2]:.0f},{cor.cmyk[3]:.0f}",
                "C": f"{cor.mistura[0]:.0f}",
                "M": f"{cor.mistura[1]:.0f}",
                "Y": f"{cor.mistura[2]:.0f}",
                "P": f"{cor.mistura[3]:.0f}",
                "B": f"{cor.mistura[4]:.0f}",
                "Área%": f"{cor.percentual:.1f}%",
            }
            if show_ml:
                ml_cor = float(total_ml) * cor.percentual / 100.0
                ml_parts = [ml_cor * m / 100.0 for m in cor.mistura]
                values.update({
                    "mlCor": f"{ml_cor:.1f}",
                    "mlC": f"{ml_parts[0]:.1f}",
                    "mlM": f"{ml_parts[1]:.1f}",
                    "mlY": f"{ml_parts[2]:.1f}",
                    "mlP": f"{ml_parts[3]:.1f}",
                    "mlB": f"{ml_parts[4]:.1f}",
                })

            for col_name, x in cols:
                if col_name == "Cor":
                    x0, x1 = x, x + 38
                    cv2.rectangle(picture, (x0, y - 16), (x1, y + 6), cor.rgb[::-1], thickness=-1)
                    cv2.rectangle(picture, (x0, y - 16), (x1, y + 6), (0, 0, 0), thickness=1)
                else:
                    cv2.putText(picture, str(values.get(col_name, "")), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 0, 0), 1, cv2.LINE_AA)

        if self.plot:
            self.plot_figure(cv2.cvtColor(picture, cv2.COLOR_BGR2RGB), "Paleta de cores")

        if self.save:
            self._ensure_output_dir()
            cv2.imwrite(os.path.join(self.output_dir, f"{self.namefile}-paleta.png"), picture)

        return picture

    def _mask_for_color(self, q8, rgb):
        return cv2.inRange(q8, np.array(rgb, dtype=np.uint8), np.array(rgb, dtype=np.uint8))

    @staticmethod
    def _contours_to_svg_path(contours, hierarchy):
        parts = []
        if hierarchy is None:
            for cnt in contours:
                if len(cnt) < 3:
                    continue
                pts = cnt[:, 0, :]
                parts.append("M " + " L ".join(f"{int(x)},{int(y)}" for x, y in pts) + " Z")
            return " ".join(parts)
        # hierarchy: [next, prev, first_child, parent]
        for i, cnt in enumerate(contours):
            if len(cnt) < 3:
                continue
            pts = cnt[:, 0, :]
            parts.append("M " + " L ".join(f"{int(x)},{int(y)}" for x, y in pts) + " Z")
        return " ".join(parts)

    def color_layer_svgs(self, largura_cm: float | None = None, altura_cm: float | None = None, incluir_numeros: bool = False):
        """Gera camadas SVG vetoriais por cor, compatíveis com corte CNC/laser.

        As dimensões físicas são embutidas no SVG (mm) quando informadas.
        """
        if self.quantified_image is None:
            return
        q8 = np.clip(np.rint(self.quantified_image).astype(np.int32), 0, 255).astype(np.uint8)
        h, w = q8.shape[:2]
        w_mm = float(largura_cm) * 10.0 if largura_cm else float(w)
        h_mm = float(altura_cm) * 10.0 if altura_cm else float(h)
        unit_w = "mm" if largura_cm else "px"
        unit_h = "mm" if altura_cm else "px"

        for cor in self.palette_data():
            rgb = tuple(int(v) for v in cor.rgb)
            mask = self._mask_for_color(q8, rgb)
            # CCOMP para preservar buracos
            cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            path_d = self._contours_to_svg_path(cnts, hier)
            hex_cor = cor.hex
            labels = []
            if incluir_numeros:
                cnts2 = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                cnts2 = cnts2[0] if len(cnts2) == 2 else cnts2[1]
                for contour in cnts2:
                    area = abs(cv2.contourArea(contour))
                    _, _, width_ctr, height_ctr = cv2.boundingRect(contour)
                    if width_ctr < 10 or height_ctr < 10 or area < 100:
                        continue
                    tx, ty = self._posicao_rotulo(contour)
                    lumin = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
                    txt_color = "#FFFFFF" if lumin < 140 else "#000000"
                    labels.append(f'<text x="{tx}" y="{ty}" font-size="12" font-family="Arial" fill="{txt_color}">{cor.numero}</text>')

            svg = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{w_mm}{unit_w}" height="{h_mm}{unit_h}" '
                f'viewBox="0 0 {w} {h}" shape-rendering="geometricPrecision">'
                f'<rect width="{w}" height="{h}" fill="white"/>'
                f'<path d="{path_d}" fill="{hex_cor}" stroke="{hex_cor}" stroke-width="0.5" fill-rule="evenodd"/>'
                + "".join(labels) +
                '</svg>'
            )
            yield {"numero": cor.numero, "nome": cor.nome, "hex": cor.hex, "rgb": rgb, "svg": svg}

    def _svg_for_mask(self, mask, cor, w, h, largura_cm=None, altura_cm=None, incluir_numeros=False):
        w_mm = float(largura_cm) * 10.0 if largura_cm else float(w)
        h_mm = float(altura_cm) * 10.0 if altura_cm else float(h)
        unit_w = "mm" if largura_cm else "px"
        unit_h = "mm" if altura_cm else "px"
        cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        path_d = self._contours_to_svg_path(cnts, hier)
        rgb = tuple(int(v) for v in cor.rgb)
        labels = []
        if incluir_numeros:
            cnts2, _ = cv2.findContours(mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
            for contour in cnts2:
                area = abs(cv2.contourArea(contour))
                _, _, width_ctr, height_ctr = cv2.boundingRect(contour)
                if width_ctr < 10 or height_ctr < 10 or area < 100:
                    continue
                tx, ty = self._posicao_rotulo(contour)
                lumin = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
                txt_color = "#FFFFFF" if lumin < 140 else "#000000"
                labels.append(f'<text x="{tx}" y="{ty}" font-size="12" font-family="Arial" fill="{txt_color}">{cor.numero}</text>')
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w_mm}{unit_w}" height="{h_mm}{unit_h}" '
            f'viewBox="0 0 {w} {h}" shape-rendering="geometricPrecision">'
            f'<rect width="{w}" height="{h}" fill="white"/>'
            f'<path d="{path_d}" fill="{cor.hex}" stroke="{cor.hex}" stroke-width="0.5" fill-rule="evenodd"/>'
            + "".join(labels) +
            '</svg>'
        )

    def color_layers(self, fundo: tuple[int, int, int] = (255, 255, 255), incluir_numeros: bool = True,
                     largura_cm: float | None = None, altura_cm: float | None = None, incluir_svg: bool = False):
        """Gera camadas separadas por cor, como mapa de camadas/topográfico.

        Cada camada tem fundo branco (ou escolhido) e apenas as regiões daquela
        cor preenchidas com a cor correspondente, opcionalmente com o número.
        """
        if self.quantified_image is None:
            return
        q8 = np.clip(np.rint(self.quantified_image).astype(np.int32), 0, 255).astype(np.uint8)
        h, w = q8.shape[:2]
        for cor in self.palette_data():
            rgb = tuple(int(v) for v in cor.rgb)
            mask = self._mask_for_color(q8, rgb)
            layer = np.empty((h, w, 3), dtype=np.uint8)
            layer[:] = np.array(fundo, dtype=np.uint8)
            layer[mask > 0] = np.array(rgb, dtype=np.uint8)

            if incluir_numeros:
                cnts = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                cnts = cnts[0] if len(cnts) == 2 else cnts[1]
                for contour in cnts:
                    area = abs(cv2.contourArea(contour))
                    _, _, width_ctr, height_ctr = cv2.boundingRect(contour)
                    if width_ctr < 10 or height_ctr < 10 or area < 100:
                        continue
                    tx, ty = self._posicao_rotulo(contour)
                    lumin = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
                    txt_color = (255, 255, 255) if lumin < 140 else (0, 0, 0)
                    cv2.putText(layer, str(cor.numero), (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.45, txt_color, 1, cv2.LINE_AA)

            item = {"numero": cor.numero, "nome": cor.nome, "hex": cor.hex, "rgb": rgb, "imagem": layer}
            if incluir_svg:
                item["svg"] = self._svg_for_mask(mask, cor, w, h, largura_cm=largura_cm, altura_cm=altura_cm, incluir_numeros=incluir_numeros)
            yield item

    def plot_figure(self, image, title):
        plt.figure(figsize=(10, 10))
        plt.axis("off")
        plt.title(title)
        if image.ndim == 2:
            plt.imshow(image, cmap="gray")
        else:
            plt.imshow(image)
        plt.tight_layout()
        plt.show()
