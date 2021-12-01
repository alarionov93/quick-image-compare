"""
Created on Tue Apr 23 13:08:33 2019

@author: dan
"""

import numpy as np
import cv2 as cv

SIZE = 8 
e = 2.78
MIN = 0.001

class NotAnImage(ValueError):
    pass

def σ(x):
    return 1 / (1 + e**(-x))

def compare(img1, img2):
    D = []
    for x in range(SIZE):
        for y in range(SIZE):
            a = σ(img1[y,x] / 255)
            b = σ(img2[y,x] / 255)
            D += [(a-b)**2]
#    print(D)
    return sum(D)**1/2

def compare_new(img1, img2):

    res = np.sum((img1-img2)**2)
    return res

def getthumb(filename):
    try:
        # print(filename)
        img = cv.imread(filename, 0)
        # print(img)
        res_im = cv.resize(img, (SIZE,SIZE))
        # print(res_im)
        # return cv.resize(cv.imread(filename, 0), (SIZE,SIZE))
        return res_im, (img.shape[1], img.shape[0])
        # return ImageOps.grayscale(Image.open(filename).resize(size = (SIZE,SIZE), resample = Image.HAMMING))
    except cv.error as e:
        print(e)
        raise NotAnImage()

if __name__ == '__main__':
    try:
        import sys
        assert len(sys.argv) > 2
        img1, img2 = sys.argv[1], sys.argv[2]
        i1 = getthumb(img1)
        i2 = getthumb(img2)
        x = compare(i1, i2)
        print("%s <=> %s (%s) %s" % (img1, img2, round(x,4), "да" if x < 0.07 else "похожи" if x < 0.7 else "нет"))
    except AssertionError:
        print("Usage")
    except FileNotFoundError:
        print("FileNotFound", file=sys.stderr)
        exit(2)