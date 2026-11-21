#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplicativo Streamlit para gerar pintura por números com paleta identificada."""

from __future__ import annotations

import io

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from canvas import Canvas

st.set_page_config(page_title="Pintura por Números", page_icon="🎨", layout="wide")

st.title("🎨 Pintura por Números com Paleta de Cores Identificada")
st.caption(
    "Envie uma imagem, escolha a quantidade de cores e gere a tela numerada, "
    "a imagem quantizada e a paleta com identificação de cor, HEX, RGB, CMYK e área."
)

with st.sidebar:
    st.header("Configurações")
    arquivo = st.file_uploader("Imagem de entrada", type=["jpg", "jpeg", "png", "webp"])
    nb_cores = st.slider("Número de cores", min_value=2, max_value=40, value=12, step=1)
    tamanho = st.slider("Maior dimensão (px)", min_value=500, max_value=4000, value=1500, step=100)
    gerar = st.button("Gerar pintura por números", type="primary", use_container_width=True)

if not arquivo:
    st.info("Carregue uma imagem na barra lateral para começar.")
    st.stop()

imagem = Image.open(arquivo).convert("RGB")
img_np = np.array(imagem)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Imagem original")
    st.image(imagem, use_container_width=True)

if not gerar:
    st.warning("Ajuste as configurações e clique em **Gerar pintura por números**.")
    st.stop()

with st.spinner("Processando imagem..."):
    tela = Canvas(img_np, nb_cores, plot=False, save=False, pixel_size=tamanho)
    tela.namefile = os_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in arquivo.name.rsplit(".", 1)[0]).strip("_") or "imagem"
    canvas_img = tela.generate()
    paleta_img = tela.display_colormap()
    paleta = tela.palette_data()

with col2:
    st.subheader("Imagem quantizada")
    st.image(tela.quantified_image, use_container_width=True)

st.subheader("Tela para pintar")
st.image(canvas_img, use_container_width=True, clamp=True)

st.subheader("Paleta de cores identificada")
linhas = []
for cor in paleta:
    linhas.append(
        {
            "Nº": cor.numero,
            "Cor": cor.nome,
            "HEX": cor.hex,
            "RGB": f"{cor.rgb[0]}, {cor.rgb[1]}, {cor.rgb[2]}",
            "CMYK (%)": f"{cor.cmyk[0]:.0f}, {cor.cmyk[1]:.0f}, {cor.cmyk[2]:.0f}, {cor.cmyk[3]:.0f}",
            "Área (%)": f"{cor.percentual:.2f}",
        }
    )
st.dataframe(linhas, use_container_width=True, hide_index=True)

cols = st.columns(min(4, len(paleta)) or 1)
for i, cor in enumerate(paleta):
    with cols[i % len(cols)]:
        swatch = np.full((70, 140, 3), cor.rgb, dtype=np.uint8)
        st.image(swatch, caption=f"{cor.numero}. {cor.nome} ({cor.hex})", use_container_width=True)

if paleta_img is not None:
    st.subheader("Mapa de paleta (imagem)")
    st.image(cv2.cvtColor(paleta_img, cv2.COLOR_BGR2RGB), use_container_width=True)

# Downloads
st.subheader("Downloads")

def img_bytes_rgb(arr_rgb, fmt="PNG"):
    buf = io.BytesIO()
    Image.fromarray(arr_rgb).save(buf, format=fmt)
    return buf.getvalue()

def img_bytes_gray(arr_gray, fmt="PNG"):
    buf = io.BytesIO()
    Image.fromarray(arr_gray).save(buf, format=fmt)
    return buf.getvalue()

csv = "numero,nome,hex,r,g,b,c,m,y,k,area_percentual\n"
for cor in paleta:
    csv += f"{cor.numero},{cor.nome},{cor.hex},{cor.rgb[0]},{cor.rgb[1]},{cor.rgb[2]},{cor.cmyk[0]},{cor.cmyk[1]},{cor.cmyk[2]},{cor.cmyk[3]},{cor.percentual}\n"

d1, d2, d3, d4 = st.columns(4)
with d1:
    st.download_button("Baixar tela (PNG)", img_bytes_gray(canvas_img), file_name=f"{os_name}-tela.png", mime="image/png", use_container_width=True)
with d2:
    st.download_button("Baixar quantizada (PNG)", img_bytes_rgb(tela.quantified_image), file_name=f"{os_name}-quantizada.png", mime="image/png", use_container_width=True)
with d3:
    if paleta_img is not None:
        st.download_button("Baixar paleta (PNG)", img_bytes_rgb(cv2.cvtColor(paleta_img, cv2.COLOR_BGR2RGB)), file_name=f"{os_name}-paleta.png", mime="image/png", use_container_width=True)
with d4:
    st.download_button("Baixar paleta (CSV)", csv.encode("utf-8"), file_name=f"{os_name}-paleta.csv", mime="text/csv", use_container_width=True)
