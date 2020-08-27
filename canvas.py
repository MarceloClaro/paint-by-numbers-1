#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to generate a canvas out of a picture"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.utils import shuffle
import cv2
import ntpath


class Canvas():
    """
    Definition of the canvas object

    Parameters
    ----------
    src : array_like
        the source picture you want to transform in a canvas
    nb_clusters :
        number of colors you want to keep
    plot : boolean, optional
        Wether you want to plot results or not
    save : boolean, optional
        Wether you want to save results or not
    pixel_size: interger, optional, default 4000
        size in pxl of the largest dimension of the ouptut canvas    
    """

    def __init__(self, path_pic, nb_color, plot=False, save=True, pixel_size=4000):
        
        self.namefile = ntpath.basename(path_pic).split(".")[0]
        self.src = cv2.cvtColor(cv2.imread(path_pic), cv2.COLOR_BGR2RGB)
        self.nb_color = nb_color
        self.plot = plot
        self.save = save
        self.tar_width = pixel_size
        self.colormap = []


    def generate(self):
        """Main function"""
        im_source = self.resize()
        clean_img = self.cleaning(im_source)
        width, height, depth = clean_img.shape
        clean_img = np.array(clean_img, dtype="uint8")/255
        quantified_image, colors = self.quantification(clean_img)
        canvas = np.ones(quantified_image.shape[:3], dtype="uint8")*255

        for ind, color in enumerate(colors):
            self.colormap.append([int(c*255) for c in color])
            mask = cv2.inRange(quantified_image, color, color)
            # cv2.imwrite(f"./outputs/canvas-{ind}.png", mask)
            # self.plot_figure(mask, f"Canvas {ind}")
            cnts = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]

            for contour in cnts:
                _, _, width_ctr, height_ctr = cv2.boundingRect(contour)
                if width_ctr > 10 and height_ctr > 10 and cv2.contourArea(contour, True) < -100:
                    cv2.drawContours(canvas, [contour], -1, 0, 1)
                    #Add label
                    txt_x, txt_y = contour[0][0]
                    cv2.putText(canvas, '{:d}'.format(ind + 1),
                                (txt_x, txt_y + 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)

        if self.plot:
            self.plot_figure(quantified_image, "Expected Result")
            self.plot_figure(canvas, "Canvas")

        if self.save:
            cv2.imwrite(f"./outputs/{self.namefile}-result.png",
                        cv2.cvtColor(quantified_image.astype('float32')*255, cv2.COLOR_BGR2RGB))
            cv2.imwrite(f"./outputs/{self.namefile}-canvas.png", canvas)
        return canvas    


    def resize(self):
        """Resize the image to match the target width and respect the picture ratio"""
        (height, width) = self.src.shape[:2]
        if height > width: #portrait mode
            dim = (int(width * self.tar_width / float(height)), self.tar_width)
        else:
            dim = (self.tar_width, int(height * self.tar_width / float(width)))
        return cv2.resize(self.src, dim, interpolation=cv2.INTER_AREA)

    def cleaning(self, picture):
        """Reduction of noize, Morphomat operations, opening then closing """
        clean_pic = cv2.fastNlMeansDenoisingColored(picture,None,10,10,7,21)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
        clean_pic = cv2.morphologyEx(clean_pic, cv2.MORPH_OPEN, kernel, cv2.BORDER_REPLICATE)
        clean_pic = cv2.morphologyEx( clean_pic, cv2.MORPH_CLOSE, kernel, cv2.BORDER_REPLICATE)
        return clean_pic

    def quantification(self, picture):
        """Returns the K-mean image"""
        width, height, dimension = tuple(picture.shape)
        image_array = np.reshape(picture, (width * height, dimension))
        image_array_sample = shuffle(image_array, random_state=0)[:1000]
        kmeans = KMeans(n_clusters=self.nb_color, random_state=42).fit(image_array_sample)
        labels = kmeans.predict(image_array)
        new_img = self.recreate_image(kmeans.cluster_centers_, labels, width, height)
        return new_img, kmeans.cluster_centers_


    def recreate_image(self, codebook, labels, width, height):
        """Create the image from a list of colors, labels and image size"""
        vfunc = lambda x: codebook[labels[x]]
        out = vfunc(np.arange(width*height))
        return np.resize(out, (width, height, codebook.shape[1]))


    def display_colormap(self):
        """Plot or save the colormap as a picture for the user"""

        picture = np.ones((len(self.colormap)*30 + 20, 300, 3), dtype="uint8")*255
        for ind, col in enumerate(self.colormap):
            cv2.putText(picture, '{:d}'.format(ind + 1),
                        (10, 30*ind + 23),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, 0, 2)
            cv2.rectangle(picture, (45, 30*ind + 5), (85, 30*ind + 25), col, thickness=-1)
            cv2.putText(picture, str(col), (100, 30*ind + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 2)
            
        if self.plot:
            self.plot_figure(picture, 'Colormap')

        if self.save:
            cv2.imwrite(f"./outputs/{self.namefile}-colormap.png", cv2.cvtColor(picture, cv2.COLOR_BGR2RGB)) 


    def plot_figure(self, image, title):
        """Function that display an image with a title and hides some stuff"""
        plt.figure()
        plt.clf()
        plt.axis('off')
        plt.title(title)
        plt.imshow(image)
        plt.show()



