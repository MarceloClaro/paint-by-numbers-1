# paint-by-numbers
A quick tool to transform any picture in a paint-by-number canvas, using opencv

# How it works
1)Picture is resized, denoised and cleaned using morphomat
2) K-mean algorythm to detect the k-colors summarizing the best the picture
3) Transform the picture to match these colors
4) Contour detection and draw on empty canvas
5) Add label in each contour
6) Creation of the colormap

# This project includes
A set of PNG pictures in `./inputs` folder, associated canvas and colormaps in the `./outputs` folder
The definition of the class Canvas in the python script `canvas.py`

### Requirements:
- Numpy
- Matplotlib
- OpenCV

### Execution:
run `python run.py [PATH_PICTURE] [NB_COLOR] [PLOT] [SAVE] [TARGET_SIZE]` 
PATH_PICTURE: path of the source picture
NB_COLOR : number of colors you want in the canvas (10 to 20)
PLOT: optional, boolean to set to True if you want to see some plots. Default False
SAVE: optional, boolean to set to True if you want to save results in the `./outputs` folder. Default True
TARGET_SIZE: interger, size in pixel of the largest dimension of the output canvas (default 4000)

### Result:

#### De Chirico, Place d'Italie, 1922
![alt text](https://github.com/Haha89/paint-by-number/blob/master/inputs/chirico.jpg "De Chirico, Place d'Italie, 1922")
#### Expected result (20 colors)
![alt text](https://github.com/Haha89/paint-by-number/blob/master/outputs/chirico-result.png "Expected result")
#### Canvas
![alt text](https://github.com/Haha89/paint-by-number/blob/master/outputs/chirico-canvas.png "Canvas")
#### Colormap
![alt text](https://github.com/Haha89/paint-by-number/blob/master/outputs/chirico-colormap.png "Colormap")

