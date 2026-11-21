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
    "a imagem quantizada e a paleta com identificação de cor, HEX, RGB, CMYK, "
    "mistura para pintura manual (Ciano, Magenta, Amarelo, Preto, Branco) e área."
)

with st.sidebar:
    st.header("Configurações")
    arquivo = st.file_uploader("Imagem de entrada", type=["jpg", "jpeg", "png", "webp"])
    nb_cores = st.slider("Número de cores", min_value=2, max_value=50, value=12, step=1)
    tamanho = st.slider("Maior dimensão (px)", min_value=500, max_value=4000, value=1500, step=100)

    st.subheader("Dimensões físicas da pintura")
    manter_proporcao = st.checkbox("Manter proporção da imagem", value=True)
    largura_cm = st.number_input("Largura (cm)", min_value=1.0, max_value=500.0, value=60.0, step=1.0)
    altura_cm_default = 60.0
    altura_cm = st.number_input("Altura (cm)", min_value=1.0, max_value=500.0, value=altura_cm_default, step=1.0, disabled=manter_proporcao)
    total_ml = st.number_input("Tinta total estimada (ml)", min_value=1.0, max_value=50000.0, value=250.0, step=10.0)
    gerar = st.button("Gerar pintura por números", type="primary", use_container_width=True)

if not arquivo:
    st.info("Carregue uma imagem na barra lateral para começar.")
    st.stop()

imagem = Image.open(arquivo).convert("RGB")
img_np = np.array(imagem)
h_img, w_img = img_np.shape[:2]

if manter_proporcao:
    altura_cm = max(1.0, min(500.0, largura_cm * (h_img / max(1, w_img))))
    st.sidebar.caption(f"Altura calculada pela proporção: {altura_cm:.1f} cm")

area_cm2 = largura_cm * altura_cm
st.sidebar.caption(f"Área da pintura: {area_cm2:.0f} cm² ({area_cm2/10000:.2f} m²)")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Imagem original")
    st.image(imagem, use_container_width=True)

if not gerar:
    st.warning("Ajuste as configurações e clique em **Gerar pintura por números**.")
    st.stop()

with st.spinner("Processando imagem..."):
    tela = Canvas(img_np, nb_cores, plot=False, save=False, pixel_size=tamanho)
    os_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in arquivo.name.rsplit(".", 1)[0]).strip("_") or "imagem"
    tela.namefile = os_name
    canvas_img = tela.generate()
    paleta_img = tela.display_colormap(total_ml=total_ml, largura_cm=largura_cm, altura_cm=altura_cm)
    paleta = tela.palette_data()

with col2:
    st.subheader("Imagem quantizada")
    st.image(tela.quantified_image, use_container_width=True)

st.subheader("Tela para pintar")
st.image(canvas_img, use_container_width=True, clamp=True)

st.subheader("Paleta de cores identificada")
st.caption(
    f"Dimensão física: {largura_cm:.1f} × {altura_cm:.1f} cm ({area_cm2/10000:.2f} m²). "
    f"Tinta total estimada: {total_ml:.1f} ml. "
    "Mistura para pintura manual: C=Ciano, M=Magenta, Y=Amarelo, P=Preto, B=Branco (percentuais heurísticos para referência)."
)
linhas = []
for cor in paleta:
    m = cor.mistura
    ml_cor = float(total_ml) * cor.percentual / 100.0
    ml_parts = [ml_cor * x / 100.0 for x in m]
    linhas.append(
        {
            "Nº": cor.numero,
            "Cor": cor.nome,
            "HEX": cor.hex,
            "RGB": f"{cor.rgb[0]}, {cor.rgb[1]}, {cor.rgb[2]}",
            "CMYK (%)": f"{cor.cmyk[0]:.0f}, {cor.cmyk[1]:.0f}, {cor.cmyk[2]:.0f}, {cor.cmyk[3]:.0f}",
            "Mistura C,M,Y,P,B (%)": f"{m[0]:.1f}, {m[1]:.1f}, {m[2]:.1f}, {m[3]:.1f}, {m[4]:.1f}",
            "Tinta cor (ml)": f"{ml_cor:.2f}",
            "ml Ciano": f"{ml_parts[0]:.2f}",
            "ml Magenta": f"{ml_parts[1]:.2f}",
            "ml Amarelo": f"{ml_parts[2]:.2f}",
            "ml Preto": f"{ml_parts[3]:.2f}",
            "ml Branco": f"{ml_parts[4]:.2f}",
            "Área (%)": f"{cor.percentual:.2f}",
        }
    )
st.dataframe(linhas, use_container_width=True, hide_index=True)

cols = st.columns(min(4, len(paleta)) or 1)
for i, cor in enumerate(paleta):
    with cols[i % len(cols)]:
        swatch = np.full((70, 140, 3), cor.rgb, dtype=np.uint8)
        ml_cor = float(total_ml) * cor.percentual / 100.0
        st.image(swatch, caption=f"{cor.numero}. {cor.nome} ({cor.hex}) - {ml_cor:.1f} ml", use_container_width=True)

if paleta_img is not None:
    st.subheader("Mapa de paleta (imagem)")
    st.image(cv2.cvtColor(paleta_img, cv2.COLOR_BGR2RGB), use_container_width=True)

st.subheader("Downloads")


def img_bytes_rgb(arr_rgb, fmt="PNG"):
    buf = io.BytesIO()
    Image.fromarray(arr_rgb).save(buf, format=fmt)
    return buf.getvalue()


def img_bytes_gray(arr_gray, fmt="PNG"):
    buf = io.BytesIO()
    Image.fromarray(arr_gray).save(buf, format=fmt)
    return buf.getvalue()


csv = "numero,nome,hex,r,g,b,c,m,y,k,ciano_pct,magenta_pct,amarelo_pct,preto_pct,branco_pct,tinta_cor_ml,ml_ciano,ml_magenta,ml_amarelo,ml_preto,ml_branco,area_percentual,largura_cm,altura_cm,area_cm2,tinta_total_ml\n"
for cor in paleta:
    mist = cor.mistura
    ml_cor = float(total_ml) * cor.percentual / 100.0
    ml_parts = [ml_cor * x / 100.0 for x in mist]
    csv += (
        f"{cor.numero},{cor.nome},{cor.hex},{cor.rgb[0]},{cor.rgb[1]},{cor.rgb[2]},"
        f"{cor.cmyk[0]},{cor.cmyk[1]},{cor.cmyk[2]},{cor.cmyk[3]},"
        f"{mist[0]},{mist[1]},{mist[2]},{mist[3]},{mist[4]},"
        f"{ml_cor:.4f},{ml_parts[0]:.4f},{ml_parts[1]:.4f},{ml_parts[2]:.4f},{ml_parts[3]:.4f},{ml_parts[4]:.4f},"
        f"{cor.percentual},{largura_cm:.2f},{altura_cm:.2f},{area_cm2:.2f},{float(total_ml):.2f}\n"
    )

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
