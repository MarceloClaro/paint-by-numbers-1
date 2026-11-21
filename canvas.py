#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geração de tela de pintura por números a partir de uma imagem."""

from __future__ import annotations

import os
from dataclasses import dataclass

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


@dataclass(frozen=True)
class CorIdentificada:
    numero: int
    nome: str
    rgb: tuple[int, int, int]
    hex: str
    cmyk: tuple[float, float, float, float]
    percentual: float


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
                        percentual=0.0,
                    )
                )
        return self.palette

    def display_colormap(self):
        palette = self.palette_data()
        if not palette:
            return None

        row_h = 34
        header_h = 42
        width = 980
        height = header_h + len(palette) * row_h + 20
        picture = np.ones((height, width, 3), dtype="uint8") * 255

        cv2.putText(picture, "Paleta de Cores Identificada", (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(picture, "Nº  Cor  Nome                HEX      RGB             CMYK(%)           Área%", (20, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (60, 60, 60), 1, cv2.LINE_AA)

        for i, cor in enumerate(palette):
            y = header_h + 30 + i * row_h
            cv2.putText(picture, f"{cor.numero:>2}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
            x0, x1 = 60, 105
            cv2.rectangle(picture, (x0, y - 18), (x1, y + 5), cor.rgb[::-1], thickness=-1)
            cv2.rectangle(picture, (x0, y - 18), (x1, y + 5), (0, 0, 0), thickness=1)
            cv2.putText(picture, cor.nome[:18], (120, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(picture, cor.hex, (330, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(picture, f"{cor.rgb[0]:>3},{cor.rgb[1]:>3},{cor.rgb[2]:>3}", (420, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cmyk = f"{cor.cmyk[0]:>4.0f},{cor.cmyk[1]:>4.0f},{cor.cmyk[2]:>4.0f},{cor.cmyk[3]:>4.0f}"
            cv2.putText(picture, cmyk, (580, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(picture, f"{cor.percentual:>5.1f}%", (800, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

        if self.plot:
            self.plot_figure(cv2.cvtColor(picture, cv2.COLOR_BGR2RGB), "Paleta de cores")

        if self.save:
            self._ensure_output_dir()
            cv2.imwrite(os.path.join(self.output_dir, f"{self.namefile}-paleta.png"), picture)

        return picture

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
