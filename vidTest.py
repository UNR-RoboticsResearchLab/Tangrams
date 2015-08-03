import numpy as np
import cv2
import copy
import time
import math

def main():
    cap = cv2.VideoCapture(0)

    peices = []
    frameCount = 0
    while(True):
        # Capture frame-by-frame
        ret, img = cap.read()

        valid = findValid(img)

        if frameCount%20 == 0:
            peices = indentifyPeices(valid, img)

        blank = np.zeros(img.shape)

        drawPieces(blank, peices)
        #drawPieces(img, peices)


        # Display the resulting frame
        cv2.imshow('blank', blank)
        cv2.imshow('frame',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

###########################################
###########################################
###########################################
###########################################
###########################################
###########################################


#TODO COMMENT
def findValid(img):
    high = {
        'green':[95,163,45],
        'yellow':[31,200,200],
        'red':[67,68,190],
        'blue':[185,70,51]
    }
    low = {
        'green':[22,37,0],
        'yellow':[0,90,90],
        'red':[5,26,108],
        'blue':[47,30,0]
    }

    valid = []
    blur = cv2.blur(img, (10,10))
    for color in high.keys():
        lower = np.array(low[color])
        upper = np.array(high[color])

        shapeMask = cv2.inRange(blur, lower, upper)
        
        #cv2.imshow(color, shapeMask)

        ret, thresh = cv2.threshold(shapeMask, 127,255,0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = reduceToBlocks(contours)
        for cont in contours:
            valid.append(cont)
    return valid


def drawPieces(img, peices):
    for peice in peices:
        peice.draw(img)

class Peice:
    def __init__(self,contour):
        self.contour = contour
        self.center = getCenter(contour)
        if (len(contour) == 4):
            if isSquare(contour):
                self.name = 'square'
            elif isRhombus(contour):
                self.name = 'rhombus'
        elif(len(contour)== 3):
            if isRightIsosceles(contour):
                self.name = 'triangle'
        if "name" in self.__dict__:
            self.theta = self.findAngleFromXaxis()
        
    #TODO COMMENT THIS FUNCTION
    def findAngleFromXaxis(self):
        xAxis = [1,0]
        if self.name == 'square':
            upperLeft = getUpperLeft(self.contour)
            lowerRight = getLowerRight(self.contour)
            v1 = np.subtract(upperLeft, lowerRight)
            ang = (py_ang(xAxis,v1)+0.75*np.pi)
            if ang > 0:
                ang -= np.pi/2
            return ang
        elif self.name == 'rhombus':
            rhombAcuteAngle = 0.729119
            v1 = np.subtract(self.contour[0], self.contour[-1])[0]
            v2 = np.subtract(self.contour[0], self.contour[1])[0]
            d1 = dist(self.contour[0], self.contour[-1])
            d2 = dist(self.contour[0], self.contour[1])
            a1 = py_ang(v1,v2)
            spin = ""
            if d1-d2 > 0:
                self.spin = "CCW"
            else:
                self.spin = "CW"
            a2 = py_ang(xAxis, v2)
            if self.spin == "CW":
                a2 += 0.75 * np.pi
            if a2 < -np.pi/2:
                a2 += np.pi
            return a2
        elif self.name == 'triangle':
            d = [0,0,0]
            for i in range(3):
                d[i] = dist(self.contour[i], self.center)
            rcIndex = d.index(min(d))
            self.rcIndex = rcIndex
            rightCorner = self.contour[rcIndex]
            nextCorner = self.contour[(rcIndex+1)%3]
            v1 = np.subtract(rightCorner, nextCorner)[0]
            ang = py_ang(np.asarray(xAxis), v1)-np.pi
            mag = abs(ang)
            sign = ang/mag
            ang = mag%(2*np.pi)
            ang *= sign
            return ang


    #Draws this shape onto the given img
    def draw(self, img):

        cv2.drawContours(img, [self.contour], -1, (125,0,0), 1)
        if "theta" in self.__dict__:
            cx, cy = self.center
            if self.theta == None: self.theta = np.pi
            cv2.ellipse(img,(int(cx),int(cy)),(10,10),0,0,self.theta*180/np.pi,(0,0,255),-1)
            '''
            if self.name == "rhombus":
                cv2.circle(img, tuple(self.contour[0][0]), 10, (255,0,0), -1)
                cv2.circle(img, tuple(self.contour[1][0]), 10, (255,0,0), -1)
            '''



def indentifyPeices(peices, img):
    pObjs = []
    for peice in peices:
        pObjs.append(Peice(peice))
    return pObjs

#Returns a tuple of the contours center coords
def getCenter(contour):
    M = cv2.moments(contour)
    cx = M['m10']/M['m00']
    cy = M['m01']/M['m00']
    return (cx,cy)

#reduces contours to the actual number of stickers identified
def reduceToBlocks(contours):
    valid = []
    #Approximate a polygon for each contour
    for cont in contours:
        eps = 0.05 * cv2.arcLength(cont, True)
        approx = cv2.approxPolyDP(cont, eps, True)
        #make sure the polygon approximated has 3 or 4 sides
        size = len(approx)
        if size == 3 or size == 4:
            valid.append(approx)
    
    contours = copy.copy(valid)
    valid = []

    #Make sure the area of the contour is roughly the correct size
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 100 and area < 100000:
            valid.append(cont)

    return valid


def dist(a,b):
    return np.linalg.norm(a-b)

def py_ang(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'    """
    cosang = np.dot(v1, v2)
    sinang = np.cross(v1, v2)
    ang = np.arctan2(sinang, cosang)
    if ang >= np.pi:
        ang -= 2*np.pi
    elif ang <= -np.pi:
        ang += 2*np.pi
    return ang

def isSquare(cont):
    if len(cont) != 4:
        return False
    for i in range(4):
        p1 = (cont[i])
        p2 = (cont[(i+1)%4])
        p3 = (cont[(i+2)%4])
        l1 = dist(p1,p2)
        l2 = dist(p2,p3)
        v1 = np.subtract(p2,p1)
        v2 = np.subtract(p2,p3)
        theta = py_ang(v1[0],v2[0])
        if abs(l2-l1) > .1*l1 and abs(theta-np.pi/2) > 0.1:
            return False
    return True

#makes the assumptions of 4 sides and not a square
def isRhombus(cont):
    aLen = getSideLengths(cont)
    for i in range(2):
        d = abs(aLen[i]-aLen[i+2])
        if d > 0.1 * aLen[i]:
            return False
    return True

#Decides if a contour is a Right angle Isosceles
#assumes 3 sides
def isRightIsosceles(cont):
    #aLen is actual Lengths
    aLen = getSideLengths(cont)
    shortest = min(aLen)
    #sLen is scaled Lengths
    sLen = [i/shortest for i in aLen]
    sLen.sort()
    rt2 = math.sqrt(2)
    if sLen[1] - 1.0 < 0.1 and abs(sLen[2]-rt2) < 0.1:
        return True


def getSideLengths(cont):
    sideLengths = []
    for i in range(len(cont)):
        length = dist(cont[i], cont[(i+1)%len(cont)])
        sideLengths.append(length)
    return sideLengths

def getLowerRight(cont):
    sums = []
    for pt in cont:
        sums.append(sum(pt[0]))
    maxVal = max(sums)
    for pt in cont:
        if sum(pt[0]) == maxVal:
            return pt[0]
    return None

def getUpperLeft(cont):
    sums = []
    for pt in cont:
        sums.append(sum(pt[0]))
    minVal = min(sums)
    for pt in cont:
        if sum(pt[0]) == minVal:
            return pt[0]
    return None


if __name__ == "__main__":
    main()
