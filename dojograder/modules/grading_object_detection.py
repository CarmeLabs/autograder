
import cv2
import numpy as np

def check_images_same(image1, image2):
    image1_cv = cv2.imread(image1)
    image2_cv = cv2.imread(image2)
    if image1_cv.shape == image2_cv.shape:
        difference = cv2.subtract( image1_cv, image2_cv)
        result = not np.any(difference)
        if result is True:
            return True
        else:
            return False
    else:
        return False

def difference(image1, image2, threshold=300000):
    image1_cv = cv2.imread(image1)
    image2_cv = cv2.imread(image2)
    if image1_cv.shape == image2_cv.shape:
        difference = cv2.subtract( image1_cv, image2_cv)
        difference = difference.sum(axis=1).sum(axis=0).sum(axis=0)
        if difference < threshold:
            return True
        else:
            return False
    else:
        return False
