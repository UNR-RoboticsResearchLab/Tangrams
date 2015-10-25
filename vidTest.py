import numpy as np
import cv2
import datetime
from Tangrams import *

def main():
    cap = cv2.VideoCapture( 0 )

    pieces = []
    connections = []
    frameCount = 0
    while( True ):
        # Capture frame-by-frame
        ret, img = cap.read()

        if frameCount%20 == 0:
            valid = findValid(img)
            pieces = indentifyPieces(valid, img)
            connections = findConnections(pieces)

        blank = np.zeros( img.shape )

        drawPieces( blank, pieces )
        drawConnections(img, connections)


        # Display the resulting frame
        cv2.imshow( 'blank', blank )
        cv2.imshow( 'frame', img )
        currentWaitKey = cv2.waitKey( 1 ) & 0xFF
        if currentWaitKey == ord( 'q' ):
            break
        if currentWaitKey == ord( 'r' ):
            writeStateToFile( pieces, connections )

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()

###########################################
###########################################
###########################################
###########################################
###########################################
###########################################

def writeStateToFile( pieces, connections ):
    currentTime = str( datetime.datetime.now() )[:-7]
    outfile = open( "state_" + currentTime, 'w+' )
    for piece in pieces:
        print "meow"
        outfile.write(piece.toString() + '\n')
    outfile.write('\n')
    for connection in connections:
        outfile.write(connection.toString() + '\n')

    outfile.close()


if __name__ == "__main__":
    main()
