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

    st.subheader("Dimensões físicas da tela")
    manter_proporcao = st.checkbox("Manter proporção da imagem", value=True)
    largura_cm = st.number_input("Largura (cm)", min_value=10.0, max_value=500.0, value=120.0, step=1.0)
    altura_cm_input = st.number_input("Altura (cm)", min_value=10.0, max_value=500.0, value=90.0, step=1.0, disabled=manter_proporcao)
    dpi = st.select_slider("Resolução de saída (DPI)", options=[72, 96, 150, 200, 300], value=150)

    st.subheader("Tinta acrílica (estimativa)")
    cobertura_ml_m2 = st.number_input("Cobertura acrílica (ml/m² por demão)", min_value=50.0, max_value=500.0, value=150.0, step=10.0)
    demaos = st.number_input("Número de demãos", min_value=1, max_value=5, value=1, step=1)
    gerar = st.button("Gerar pintura por números", type="primary", width='stretch')

if not arquivo:
    st.info("Carregue uma imagem na barra lateral para começar.")
    st.stop()

imagem = Image.open(arquivo).convert("RGB")
img_np = np.array(imagem)
h_img, w_img = img_np.shape[:2]

if manter_proporcao:
    altura_cm = max(10.0, min(500.0, largura_cm * (h_img / max(1, w_img))))
else:
    altura_cm = max(10.0, min(500.0, float(altura_cm_input)))

area_cm2 = largura_cm * altura_cm
area_m2 = area_cm2 / 10000.0
total_ml = area_m2 * float(cobertura_ml_m2) * int(demaos)

# Tamanho em pixels baseado na dimensão física e DPI
largura_px = round(largura_cm / 2.54 * float(dpi))
altura_px = round(altura_cm / 2.54 * float(dpi))
tamanho_px = max(largura_px, altura_px)
tamanho_px = max(500, min(8000, tamanho_px))

st.sidebar.markdown("---")
st.sidebar.markdown("**Valores calculados automaticamente**")
st.sidebar.write(f"Largura: **{largura_cm:.1f} cm** ({largura_cm/100:.2f} m)")
st.sidebar.write(f"Altura: **{altura_cm:.1f} cm** ({altura_cm/100:.2f} m)")
st.sidebar.write(f"Área: **{area_cm2:.0f} cm²** ({area_m2:.2f} m²)")
st.sidebar.write(f"Resolução: **{dpi} DPI** → **{largura_px} × {altura_px} px**")
st.sidebar.write(f"Tinta acrílica estimada: **{total_ml:.1f} ml** ({demaos} demão{'s' if int(demaos)>1 else ''}, {cobertura_ml_m2:.0f} ml/m²/demão)")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Imagem original")
    st.image(imagem, width='stretch')

if not gerar:
    st.warning(f"Ajuste as configurações e clique em **Gerar pintura por números**. Saída calculada: {largura_px}×{altura_px} px ({dpi} DPI) para {largura_cm:.1f}×{altura_cm:.1f} cm, tinta estimada {total_ml:.1f} ml.")
    st.stop()

with st.spinner("Processando imagem..."):
    tela = Canvas(img_np, nb_cores, plot=False, save=False, pixel_size=tamanho_px)
    os_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in arquivo.name.rsplit(".", 1)[0]).strip("_") or "imagem"
    tela.namefile = os_name
    canvas_img = tela.generate()
    paleta_img = tela.display_colormap(total_ml=total_ml, largura_cm=largura_cm, altura_cm=altura_cm, dpi=int(dpi))
    paleta = tela.palette_data()

with col2:
    st.subheader("Imagem quantizada")
    st.image(tela.quantified_image, width='stretch')

st.subheader("Tela para pintar")
st.image(canvas_img, width='stretch', clamp=True)

st.subheader("Paleta de cores identificada")
st.caption(
    f"Dimensão física: {largura_cm:.1f} × {altura_cm:.1f} cm ({area_cm2/10000:.2f} m²) | "
    f"Resolução: {dpi} DPI ({largura_px} × {altura_px} px) | "
    f"Tinta acrílica estimada: {total_ml:.1f} ml ({demaos} demão{'s' if int(demaos)>1 else ''}). "
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
st.dataframe(linhas, width='stretch', hide_index=True)

cols = st.columns(min(4, len(paleta)) or 1)
for i, cor in enumerate(paleta):
    with cols[i % len(cols)]:
        swatch = np.full((70, 140, 3), cor.rgb, dtype=np.uint8)
        ml_cor = float(total_ml) * cor.percentual / 100.0
        st.image(swatch, caption=f"{cor.numero}. {cor.nome} ({cor.hex}) - {ml_cor:.1f} ml", width='stretch')

if paleta_img is not None:
    st.subheader("Mapa de paleta (imagem)")
    st.image(cv2.cvtColor(paleta_img, cv2.COLOR_BGR2RGB), width='stretch')

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
    st.download_button("Baixar tela (PNG)", img_bytes_gray(canvas_img), file_name=f"{os_name}-tela.png", mime="image/png", width='stretch')
with d2:
    st.download_button("Baixar quantizada (PNG)", img_bytes_rgb(tela.quantified_image), file_name=f"{os_name}-quantizada.png", mime="image/png", width='stretch')
with d3:
    if paleta_img is not None:
        st.download_button("Baixar paleta (PNG)", img_bytes_rgb(cv2.cvtColor(paleta_img, cv2.COLOR_BGR2RGB)), file_name=f"{os_name}-paleta.png", mime="image/png", width='stretch')
with d4:
    st.download_button("Baixar paleta (CSV)", csv.encode("utf-8"), file_name=f"{os_name}-paleta.csv", mime="text/csv", width='stretch')
