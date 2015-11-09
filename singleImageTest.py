import numpy as np
import cv2
import sys  
from Tangrams import *
from TangramsGraph import *

def main():

    if len(sys.argv) > 2:
        filename1 = sys.argv[1]
        filename2 = sys.argv[2]
    else:
        print("Invalid input")
        sys.exit()

    g = makeGraphFromImage(filename1)
    f = makeGraphFromImage(filename2)

    graphTest(f, g)

    cv2.waitKey(0)

    # When everything is done, shutdown.
    cv2.destroyAllWindows()
    

###########################################
###########################################
###########################################
###########################################
###########################################
###########################################

def makeGraphFromImage(filename):
    img = cv2.imread(filename, 1)

    #Create Empty lists for pieces and connections.
    pieces = []
    connections = []

    #Find pieces and connections.
    valid = findValid(img)
    pieces = indentifyPieces(valid, img)
    connections = findConnections(pieces)

    #Create blank image to draw on.
    blank = np.zeros(img.shape)

    #Draw pieces and connections.
    drawPieces(blank, pieces)
    drawConnections(img, connections)


    # Display the resulting images.
    cv2.imshow('blank '+filename, blank)
    cv2.imshow('frame '+filename, img)


    g = makeGraph(pieces, connections)
    return g

def graphTest(f, g):
    if f == g:
        print("They match.")
    else:
        print("They don't match.")






if __name__ == "__main__":
    main()
