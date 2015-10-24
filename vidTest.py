import numpy as np
import cv2
import copy
import time
import math
from Tangrams import *

def main():
    cap = cv2.VideoCapture(0)

    pieces = []
    frameCount = 0
    while(True):
        # Capture frame-by-frame
        ret, img = cap.read()

        valid = findValid(img)

        if frameCount%20 == 0:
            pieces = indentifyPieces(valid, img)

        blank = np.zeros(img.shape)

        drawPieces(blank, pieces)
        #drawPieces(img, pieces)


        # Display the resulting frame
        cv2.imshow('blank', blank)
        cv2.imshow('frame',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()

###########################################
###########################################
###########################################
###########################################
###########################################
###########################################



if __name__ == "__main__":
    main()
