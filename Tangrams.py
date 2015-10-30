#!/usr/bin/python

import numpy as np
import cv2
import copy
import time
import math

NON_CONNECTION = 0
SIDE_SIDE = 1
SIDE_POINT = 2
POINT_POINT = 3


class Connection:

    def __init__(self, piece1, piece2):
        self.pieces = [piece1, piece2]
        self.determineConnectionType()

    #TODO COMMENT / IMPROVE
    def determineConnectionType(self):
        self.connectionType = NON_CONNECTION
        #Loop for each side of the first piece.
        for side in self.pieces[0].sides:
            #Loop for each side in the second piece.
            for otherSide in self.pieces[1].sides:
                if side.isParallel(otherSide):
                    #Distance from other center to side
                    d1 = side.distanceTo(otherSide.center)
                    #Distance from other side to center
                    d2 = otherSide.distanceTo(side.center)
                    #Distance between centers
                    dCenters= dist(side.center, otherSide.center)
                    if d1 < 20 and d2 < 20 and dCenters <= 50:
                        self.connectionType = SIDE_SIDE
                        self.touching = [side, otherSide]
                        return
            #Loop for each point in the second piece.
            for otherPoint in self.pieces[1].contour:
                #distance from point to line
                d1 = side.distanceTo(otherPoint)
                #distance from point to center of line
                d2 = dist(otherPoint, side.center)
                if d1 < 20 and d2 < side.length/2.0 :
                    self.connectionType = SIDE_POINT
                    self.touching = [Point(otherPoint), side]
                    return
        #Loop for each point in the first piece.
        for point in self.pieces[0].contour:
            #Loop for point in the second piece.
            for otherPoint in self.pieces[1].contour:
                #distance between points
                distance = dist(point[0], otherPoint[0])
                if distance < 25:
                    self.connectionType = POINT_POINT
                    self.touching = [Point(point), Point(otherPoint)]
                    return
            #Loop for each side in the second piece.
            for otherSide in self.pieces[1].sides:
                #distance from point to line
                d1 = otherSide.distanceTo(point)
                #distance from point to center of line
                d2 = dist(point, otherSide.center)
                if d1 < 20 and d2 < otherSide.length/2.0 :
                    self.connectionType = SIDE_POINT
                    self.touching = [Point(point), otherSide]
                    return

    #Draws the connection to the given image.
    def draw(self, img):
        drawColors = {
                    SIDE_SIDE: (255, 0, 0),
                    SIDE_POINT: (0, 255, 0),
                    POINT_POINT: (0, 0, 255)
                    }
        color = drawColors[self.connectionType]
        self.touching[0].draw(img, color)
        self.touching[1].draw(img, color)

    def isSimilar(self, other):
        #Same connection type.
        if(self.connectionType == other.connectionType):
            if( 
                (   #self first matches other first.
                    self.pieces[0].name == other.pieces[0].name
                    and
                    #self second matches other second.
                    self.pieces[1].name == other.pieces[1].name
                )
                or
                (   #self first matches other second.
                    self.pieces[0].name == other.pieces[1].name
                    and
                    #self second matches other first.
                    self.pieces[1].name == other.pieces[0].name
                )
               ):
                return True
        return False

    def __str__(self):
        string = ""
        ConnectionTypes = {
            SIDE_SIDE: "SIDE-SIDE",
            SIDE_POINT: "SIDE-POINT",
            POINT_POINT: "POINT_POINT"
        }
        string = ConnectionTypes[self.connectionType] + '\n'
        piece1 = self.pieces[0]
        piece2 = self.pieces[1]

        string += "\t" + str(piece1) + '\n'
        string += "\t" + str(piece2) + '\n'
        return string

class Point:
    def __init__(self, pt):
        self.pt = pt

    #Draws the point to the given image with the given color.
    def draw(self, img, color):
        cv2.circle(img, tuple(self.pt[0]), 4, color, -1)

    def __str__(self):
        return str( np.asarray(self.pt) )

class Line:
    def __init__(self,pts):
        self.pts = pts
        pt1, pt2 = pts
        self.length = dist(pt1, pt2)
        self.center = (pt1 + pt2) / 2
        dx = pt2[0] - pt1[0]
        dy = pt2[1] - pt1[1]
        self.slope = np.arctan((pt2[1] - pt1[1]) / (pt2[0] - pt1[0]))

    #Returns true if the two lines are parallel.
    def isParallel(self, otherLine):
        if abs(self.slope - otherLine.slope) < 0.15:
            return True
        else:
            return False
    
    #Returns the distance from the line to the point.
    def distanceTo(self, point):
        #Uses A = 0.5*B*H ==> H = 2*A/B
        triangle = np.float32(np.vstack((self.pts, point)))
        area = cv2.contourArea(triangle)
        distance = 2.0 * area / self.length
        return distance

    def draw(self, img, color = (10,55,10)):
        cv2.line(img, tuple(self.pts[0]), tuple(self.pts[1]), color, 2)

    def __str__(self):
        return str( np.asarray(self.pts))

class Piece:
    def __init__(self, contour):
        self.contour = contour
        self.center = getCenter(contour)
        fCont = np.float32(contour)
        self.sides = [Line([fCont[i][0], fCont[(i + 1) % len(contour)][0]])
                     for i in range(len(contour))]

        #Determines the name of the piece.
        if (len(contour) == 4):
            if isSquare(contour):
                self.name = 'square'
            elif isParallelogram(contour):
                self.name = 'parallelogram'
        elif(len(contour)== 3):
            if isRightIsosceles(contour):
                self.name = 'triangle'

        if "name" in self.__dict__:
            self.theta = self.findAngleFromXaxis()
        
    #Finds the angle form the x - axis.
    def findAngleFromXaxis(self):
        xAxis = [1, 0]
        ### SQUARE ###
        if self.name == 'square':
            upperLeft = getUpperLeft(self.contour)
            lowerRight = getLowerRight(self.contour)
            #Vector from upper-left to lower-right
            diagonal = np.subtract(upperLeft, lowerRight)
            # The angle is adjusted by 0.75*PI to give us the angle of the
            # 'topside' from the x-axis.
            ang = (angleBetween(xAxis, diagonal) + 0.75 * np.pi)
            # Adjust the angle to account for symmetry of square.
            if ang > 0:
                ang -= np.pi / 2
            return ang
        ### PARALLELOGRAM ###
        elif self.name == 'parallelogram':
            # Assumes a parallelogram with a small angle of PI/4
            #v1 and v2 are the vectors from the '0' along the edges of the piece.
            v1 = np.subtract(self.contour[0], self.contour[-1])[0]
            v2 = np.subtract(self.contour[0], self.contour[1])[0]
            # d1 and d2 are the magnitudes of the vectors v1 and v2 respectively.
            d1 = dist(self.contour[0], self.contour[-1])
            d2 = dist(self.contour[0], self.contour[1])
            a2 = angleBetween(xAxis, v2)

            # Determines the spin of parallelogram.
            if d1 - d2 > 0:
                self.spin = "CCW"
            else:
                self.spin = "CW"

            # Makes appropriate correction for symmetry and spin.
            if self.spin == "CW":
                a2 += 0.75 * np.pi
            if a2 < -np.pi / 2:
                a2 += np.pi
            return a2

        ### TRIANGLE ###
        elif self.name == 'triangle':
            distancesFromCenter = [0, 0, 0]

            # Determine the distances from corner to center.
            # The smallest of these must be the corner that is a right triangle.
            # Assumes a right isosceles triangle.
            for i in range(3):
                distancesFromCenter[i] = dist(self.contour[i], self.center)
            rcIndex = distancesFromCenter.index(min(distancesFromCenter))
            self.rcIndex = rcIndex
            rightCorner = self.contour[rcIndex]
            nextCorner = self.contour[(rcIndex + 1) % 3]

            # v1 is the vector between the right-angled corner and it's clockwise? neighbor.
            v1 = np.subtract(rightCorner, nextCorner)[0]
            ang = angleBetween(np.asarray(xAxis), v1) - np.pi
            mag = abs(ang)
            sign = ang / mag
            ang = mag % (2 * np.pi)
            ang *= sign
            return ang


    #Draws this shape onto the given img
    def draw(self, img):
        cv2.drawContours(img, [self.contour], -1, (125, 0, 0), 1)

        if "theta" in self.__dict__:
            cx, cy = self.center

            color = (0, 0, 255)
            center = (int(cx), int(cy))
            startAngle = 0
            endAngle = self.theta * (180 / np.pi)
            radii = (10, 10)

            if self.theta == None:
                self.theta = np.pi
                color = (255, 255, 255)

            cv2.ellipse(img, center, radii, 0, startAngle, endAngle, color, -1)
            '''
            if self.name == "rhombus":
                cv2.circle(img, tuple(self.contour[0][0]), radii[0], color, -1)
                cv2.circle(img, tuple(self.contour[1][0]), radii[0], color, -1)
            '''

    def __str__(self):
        string = self.name + " "
        string += str(round(self.theta, 2)) + " "
        string += str(round(self.center[0],2)) + " "
        string += str(round(self.center[1],2))
        return string

def drawConnections(img, connections):
    for connection in connections:
        connection.draw(img)

def drawPieces(img, pieces):
    for piece in pieces:
        piece.draw(img)

def drawLines(img, pieces):
    for piece in pieces:
        for side in piece.sides[:1]:
            side.draw(img)

def removeDuplicates(contours):
    centers = []
    valid = []
    #SOMETHING HERE IS WRONG NOT SURE WHAT
    for cont in contours:
        if len(centers) > 0:
            center = getCenter(cont)
            distances = [dist(np.asarray(i),np.asarray(center)) for i in centers]
            #print distances
            smallest = min(distances)
            if smallest > 20:
                valid.append(cont)
                centers.append(center)
        else:
            valid.append(cont)
            centers.append(getCenter(cont))
            #print centers, "***"
    #print centers
    #print ""
    return valid

#Returns the valid connections between the given pieces.
def findConnections(pieces):
    connections = []
    if len( pieces) > 1:
        for i in range(len(pieces) - 1):
            for other in pieces[i + 1:]:
                center1 = np.asarray(pieces[i].center)
                center2 = np.asarray(other.center)
                d = dist(center1, center2)
                if d < 250:
                    connections.append(Connection(pieces[i], other))
    #Remove non-connections from list
    connections = [i for i in connections if i.connectionType != NON_CONNECTION]
    return connections

#Returns a list of contours from given image that should be pieces.
def findValid(img):
    #Upper and lower bounds for the colors of the pieces.
    high, low = getColors(img)

    valid = []
    blur = cv2.blur(img, (10, 10))
    for color in high.keys():
        lower = np.array(low[color])
        upper = np.array(high[color])

        #shapeMask of pixels that fit current criteria.
        shapeMask = cv2.inRange(img, lower, upper)
        
        #cv2.imshow(color, shapeMask)

        ret, thresh = cv2.threshold(shapeMask, 127, 255, 0)
        _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = reduceToBlocks(contours)
        for cont in contours:
            valid.append(cont)
    valid = removeDuplicates(valid)
    return valid

# TODO Make this less lighting dependant (HSV?) Better name?
def getColors(img):
    #BGR VALUES
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
    return high, low

#Draws the given list of pieces onto the given image.
def drawPieces(img, pieces):
    for piece in pieces:
        piece.draw(img)

#Return a list of piece objects made from the given list of contours.
def indentifyPieces(contours, img):
    pObjs = []
    for cont in contours:
        pObjs.append(Piece(cont))
    return pObjs

#Returns a tuple of the contour's center coords.
def getCenter(contour):
    M = cv2.moments(contour)
    cx = M['m10'] / M['m00']
    cy = M['m01'] / M['m00']
    return (cx, cy)

#Reduces contours to the actual number of stickers identified
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

#Retruns the Euclidian distance between two points.
def dist(a, b):
    return np.linalg.norm(a - b)

#Returns the angle in radians between the two given vectors.
def angleBetween(v1, v2):
    cosang = np.dot(v1, v2)
    sinang = np.cross(v1, v2)
    ang = np.arctan2(sinang, cosang)
    if ang >= np.pi:
        ang -= 2 * np.pi
    elif ang <= -np.pi:
        ang += 2 * np.pi
    return ang

#Decides if the given contour is a square.
def isSquare(cont):
    if len(cont) != 4:
        return False
    for i in range(4):
        #Pick three corners.
        p1 = (cont[i])
        p2 = (cont[(i + 1) % 4])
        p3 = (cont[(i + 2) % 4])
        #Find lengths of sides.
        l1 = dist(p1, p2)
        l2 = dist(p2, p3)
        #Vectors from middle point to neighbors.
        v1 = np.subtract(p2, p1)
        v2 = np.subtract(p2, p3)
        theta = angleBetween(v1[0], v2[0])
        if abs(l2 - l1) > .1 * l1 and abs(theta - np.pi / 2) > 0.1:
            return False
    return True

#Decides if a contour is a parallelogram.
#Makes the assumptions of 4 sides and not a square.
def isParallelogram(cont):
    aLen = getSideLengths(cont)
    for i in range(2):
        d = abs(aLen[i] - aLen[i + 2])
        if d > 0.1 * aLen[i]:
            return False
    return True

#Decides if a contour is a Right angle Isosceles
#Assumes 3 sides.
def isRightIsosceles(cont):
    #aLen is actual Lengths
    aLen = getSideLengths(cont)
    shortest = min(aLen)
    #sLen is scaled Lengths
    sLen = [i / shortest for i in aLen]
    sLen.sort()
    rt2 = math.sqrt(2)
    if sLen[1] - 1.0 < 0.1 and abs(sLen[2] - rt2) < 0.1:
        return True

#Returns a list of lengths of each side of the given contour.
def getSideLengths(cont):
    sideLengths = []
    for i in range(len(cont)):
        length = dist(cont[i], cont[(i + 1) % len(cont)])
        sideLengths.append(length)
    return sideLengths

#Returns the lowest right most corner by comparing the sum of x and y positions.
def getLowerRight(cont):
    sums = []
    for pt in cont:
        sums.append(sum(pt[0]))
    maxVal = max(sums)
    for pt in cont:
        if sum(pt[0]) == maxVal:
            return pt[0]
    return None

#Returns the upper left most corner by comparing the sum of x and y positions.
def getUpperLeft(cont):
    sums = []
    for pt in cont:
        sums.append(sum(pt[0]))
    minVal = min(sums)
    for pt in cont:
        if sum(pt[0]) == minVal:
            return pt[0]
    return None
