#!/usr/bin/python

import numpy as np
import cv2
import copy
import time

def main():
    num = 3
    img = cv2.imread('Images/Tan%i.jpg'%num)
    

    high = {
        'green':[55,63,15],
        'yellow':[43,125,195],
        'red':[37,50,160],
        'blue':[85,51,51]
    }
    low = {
        'green':[22,37,0],
        'yellow':[20,106,164],
        'red':[5,26,108],
        'blue':[47,30,0]
    }

    
    valid = []

    blur = cv2.blur(img, (10,10))
    for color in high.keys():
        lower = np.array(low[color])
        upper = np.array(high[color])

        shapeMask = cv2.inRange(blur, lower, upper)
        cv2.imshow('mask', shapeMask)
        cv2.waitKey(0)
        ret, thresh = cv2.threshold(shapeMask, 127,255,0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = reduceToBlocks(contours)
        for cont in contours:
            valid.append(cont)


    cv2.drawContours(img, valid, -1, (125,0,0), 1)

    indentifyPeices(valid, img)


    cv2.imshow('img', img)
    cv2.waitKey(0)
    

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
        
    def findAngleFromXaxis(self):
        if self.name == 'square':
            upperLeft = getUpperLeft(self.contour)
            lowerRight = getLowerRight(self.contour)
            v1 = [1,0]
            v2 = np.subtract(upperLeft, lowerRight)
            return py_ang(v1,v2)-(3.0/4.0) * np.pi
        elif self.name == 'rhombus':
            rhombAcuteAngle = 0.729119
            v1 = np.subtract(self.contour[0], self.contour[-1])[0]
            v2 = np.subtract(self.contour[0], self.contour[1])[0]
            return (py_ang(v1,v2))
        elif self.name == 'triangle':
            pass

def indentifyPeices(peices, img):
    pObjs = []
    for peice in peices:
        pObjs.append(Peice(peice))
    for peice in pObjs:
        #print peice.__dict__
        if "name" in peice.__dict__ and peice.theta != None:
            cx, cy = peice.contour[0][0]
            print peice.theta
            cv2.ellipse(img,(int(cx),int(cy)),(20,20),0,0,peice.theta*180/np.pi,255,-1)
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
    for cont in contours:
        eps = 0.05 * cv2.arcLength(cont, True)
        approx = cv2.approxPolyDP(cont, eps, True)
        #if len(approx) == 4:
        valid.append(approx)
    
    contours = copy.copy(valid)
    valid = []
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 100 and area < 100000:
            valid.append(cont)

    return valid


def dist(a,b):
    return np.linalg.norm(a-b)

#Found this
def py_ang(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'    """
    cosang = np.dot(v1, v2)
    sinang = np.linalg.norm(np.cross(v1, v2))
    return np.arctan2(sinang, cosang)

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
    print("romb")
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
