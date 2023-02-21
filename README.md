#Pintura por números
Uma ferramenta Python rápida para transformar qualquer imagem em uma tela de pintura por número, usando opencv

Como funciona
A imagem é redimensionada, desnoizada e limpa usando morfomata
Algoritmo K-mean para detectar as k-cores resumindo o melhor da imagem
Transformação da imagem para corresponder a essas cores
Detecção de contorno e desenho de contornos em nova tela
Adicionar rótulo de cada forma na tela de desenho
Criação do mapa de cores para o usuário
Este projeto inclui
Um conjunto de imagens PNG na pasta, tela associada e mapas de cores na pasta A definição da classe Canvas no ./inputs./outputsscript python canvas.py

Requisitos:
Numpy
Matplotlib •
OpenCV

Execução:
executar com:python run.py [path] [nb_color] [plot] [save] [pixel_size]

caminho: caminho da imagem de origem nb_color : número de cores desejadas no gráfico de tela (10 a 20):
opcional, booleano a ser definido como Verdadeiro se você quiser ver alguns gráficos. 
Salvamento falso padrão: opcional, booleano para definir como Verdadeiro se você quiser salvar os resultados na pasta. True pixel_size padrão: opcional, interger, tamanho em pixel da maior dimensão da tela de saída (padrão 4000)./outputs
