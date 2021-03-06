#!/usr/bin/python

import numpy as np
import cv2
import copy
import time
import math

NON_CONNECTION = -1
SIDE_SIDE = 0
SIDE_POINT = 1
POINT_POINT = 2

MAX_POINT_POINT_DIST = 25
MAX_SIDE_CENTER_DIST = 20
MAX_POINT_SIDE_DIST = 20
MAX_CENTER_DIST = 50
MAX_ANG_DIFF = 0.5
MAX_CONNECTION_DIST = 250

class Connection:

    def __init__(self, piece1, piece2):
        self.pieces = [piece1, piece2]
        self.determineConnectionType()

    #Determines the type of connection this is.
    def determineConnectionType(self):
        #Innocent of connection-ness until proven connected.
        self.connectionType = NON_CONNECTION
        #Loop for each side of the first piece.
        for side in self.pieces[0].sides:
            #Looking for SIDE_SIDE
            for otherSide in self.pieces[1].sides:
                if( self.isSideSideConnection(side, otherSide) ):
                    self.connectionType = SIDE_SIDE
                    self.touching = [side, otherSide]
                    #Retrieve and store location numbers.
                    self.locationNumbers = [
                        self.pieces[0].getLocationNumber(side),
                        self.pieces[1].getLocationNumber(otherSide)
                    ]
                    # print("Location numbers SIDE_SIDE")
                    # print( self.locationNumbers )
                    return

            #Looking for SIDE_POINT
            for otherPoint in self.pieces[1].contour:
                if( self.isSidePointConnection(side, otherPoint) ):
                    self.connectionType = SIDE_POINT
                    self.touching = [Point(otherPoint), side]
                    #Retrieve and store location numbers.
                    self.locationNumbers = [
                        self.pieces[0].getLocationNumber(side),
                        self.pieces[1].getLocationNumber(otherPoint)
                    ]
                    # print("Location numbers SIDE_POINT")
                    # print( self.locationNumbers )
                    return

        #Loop for each point in the first piece.
        for point in self.pieces[0].contour:
            #Looking for POINT_POINT connection.
            for otherPoint in self.pieces[1].contour:
                if( self.isPointPointConnection(point, otherPoint) ):
                    self.connectionType = POINT_POINT
                    self.touching = [Point(point), Point(otherPoint)]
                    #Retrieve and store location numbers.
                    self.locationNumbers = [
                        self.pieces[0].getLocationNumber(point),
                        self.pieces[1].getLocationNumber(otherPoint)
                    ]
                    # print("Location numbers POINT_POINT")
                    # print( self.locationNumbers )
                    return

            #Looking for a SIDE_POINT connection.
            for otherSide in self.pieces[1].sides:
                if( self.isSidePointConnection(otherSide, point) ):
                    self.connectionType = SIDE_POINT
                    self.touching = [Point(point), otherSide]
                    #Retrieve and store location numbers.
                    self.locationNumbers = [
                        self.pieces[0].getLocationNumber(point),
                        self.pieces[1].getLocationNumber(otherSide)
                    ]
                    # print("Location numbers POINT_SIDE")
                    # print( self.locationNumbers )
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

    def isPointPointConnection(self, point1, point2):
        #distance between points
        distance = dist(point1[0], point2[0])
        if(distance < MAX_POINT_POINT_DIST):
            return True
        return False

    def isSidePointConnection(self, side, point):
        #Distance from point to side.
        distPointSide = side.distanceTo(point)
        #Distance from point to center of the side.
        distPointSidesCenter = dist(point, side.center)

        if(     distPointSide < MAX_POINT_SIDE_DIST
            and distPointSidesCenter < side.length / 2.0
            ):
            return True
        return False

    def isSideSideConnection(self, side1, side2):
        if side1.isParallel(side2):
            #Distance from other center to side
            distCenterSide = side1.distanceTo(side2.center)
            #Distance from other side to center
            distSideCenter = side2.distanceTo(side1.center)
            #Distance between centers
            distBetweenCenters= dist(side1.center, side2.center)

            if(     distCenterSide < MAX_SIDE_CENTER_DIST
                and distSideCenter < MAX_SIDE_CENTER_DIST 
                and distBetweenCenters < MAX_CENTER_DIST
                ):
                return True
        return False

    def isSimilar(self, other):
        #Same connection type.
        if(self.connectionType == other.connectionType):
            if(     (   #self first matches other first.
                        self.pieces[0].name == other.pieces[0].name
                        #self second matches other second. 
                    and self.pieces[1].name == other.pieces[1].name
                        #has same side/corner numbers
                    and self.hasSameLocationNumbers(other, 0, 0)
                    and self.hasSameLocationNumbers(other, 1, 1)
                    )
                or  (   #self first matches other second.
                        self.pieces[0].name == other.pieces[1].name
                        #self second matches other first.
                    and self.pieces[1].name == other.pieces[0].name
                        #has same side/corner numbers
                    and self.hasSameLocationNumbers(other, 0, 1)
                    and self.hasSameLocationNumbers(other, 1, 0)
                    )
                ):
                return True
        return False

    def hasSameLocationNumbers(self, other, selfIndex, otherIndex):
        return(     self.locationNumbers[selfIndex]
                == other.locationNumbers[otherIndex] )

    def __str__(self):
        string = ""
        ConnectionTypes = {
            SIDE_SIDE: "SIDE_SIDE",
            SIDE_POINT: "SIDE_POINT",
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

        self.name = "NON_PIECE"

        #Determines the name of the piece.
        if (len(contour) == 4):
            if self.isSquare():
                self.name = 'square'
                self.hasSymmetry = True
            elif self.isParallelogram():
                self.name = 'parallelogram'
                self.hasSymmetry = True
        elif(len(contour)== 3):
            if self.isRightIsosceles():
                self.name = 'triangle'
                self.hasSymmetry = False

        if "name" in self.__dict__:
            self.theta = self.findAngleFromXaxis()

    #Finds the angle form the x - axis.
    def findAngleFromXaxis(self):
        xAxis = [1, 0]
        ### SQUARE ###
        if self.name == 'square':
            return self.findSquareAngleFromAxis()
        ### PARALLELOGRAM ###
        elif self.name == 'parallelogram':
            return self.findParallelogramAngleFromAxis()
        ### TRIANGLE ###
        elif self.name == 'triangle':
            return self.findTriangleAngleFromAxis()

    def findSquareAngleFromAxis(self):
        xAxis = [1, 0]
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

    def findParallelogramAngleFromAxis(self):
        xAxis = [1, 0]
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

    def findTriangleAngleFromAxis(self):
        xAxis = [1, 0]
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

        # v1 is the vector between the right-angled corner and it's
        # clockwise? neighbor.
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

        if "theta" in self.__dict__ and self.theta != None:
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
        string = str(round(self.theta, 2)) + " "
        string += str(round(self.center[0], 2)) + " "
        string += str(round(self.center[1], 2))
        return string

    def getAngleAtVertex(self, vertex):
        vertexIndex = self.getIndexOfVertex(vertex)
        #Get neighbors' index.
        previousNeighbor = (vertexIndex - 1) % len(self.contour)
        nextNeighbor = (vertexIndex + 1) % len(self.contour)
        #Get vectors to neighbors.
        toPreviousNeighbor = (self.contour[previousNeighbor] - vertex)[0];
        toNextNeighbor = (self.contour[nextNeighbor] - vertex)[0];
        #Return angle between neighbors.
        return angleBetween(toPreviousNeighbor, toNextNeighbor)

    def getIndexOfVertex(self, vertex):
        for i in range(len(self.contour)):
            if all( (self.contour[i] == vertex)[0]):
                return i

    def getLocationNumber(self, contact):
        ### SQUARE ###
        if self.name == 'square':
            # print "getting locationNumbers of square"
            #Returns -1 because which point doesn't matter on a square.
            return -1
        ### PARALLELOGRAM ###
        elif self.name == 'parallelogram':
            # print "getting locationNumbers of parallelogram"
            return self.getLocationNumberOfParallelogram(contact)
        ### TRIANGLE ###
        elif self.name == 'triangle':
            # print "getting locationNumbers of triangle"
            return self.getLocationNumberOfTriangle(contact)
    
    def getLocationNumberOfParallelogram(self, contact):
        locationNum = None
        
        if(isinstance(contact, Line)):
            #Calculate line Nums for CW
            sideLengths = self.getSideLengths()
            sideLengths.sort()

            if( contact.length in sideLengths[:2] ):
                locationNum = 1
            else:
                locationNum = 2

            if self.spin != "CW":
                locationNum += 2

            return locationNum
        else:
            #Calculate point Nums for CW
            vertexAngles = self.getVertexAngles()
            vertexAngles.sort()
            contactAngle = self.getAngleAtVertex(contact)

            if( contactAngle in vertexAngles[:2] ):
                locationNum = 1
            else:
                locationNum = 2

            if self.spin != "CW":
                locationNum += 2

            return locationNum

    def getLocationNumberOfTriangle(self, contact):
        if(isinstance(contact, Line)):
            #Calculate line NUMS for Triangle
            sideLengths = self.getSideLengths()
            largestSideIndex = sideLengths.index(max(sideLengths))
            #Mod 3 to loop around triangle if out of bounds.
            largesstSideNeighborIndex = (largestSideIndex + 1) % 3;
            if(contact.length == sideLengths[largestSideIndex]):
                return 1
            elif(contact.length == sideLengths[largesstSideNeighborIndex]):
                return 2
            else:
                return 3

        else:
            #Calculate point NUMS for Triangle
            vertexIndex = self.getIndexOfVertex(contact)
            #Mod 3 to loop around the triangle if index gets too large.
            nextVertexIndex = (vertexIndex + 1) % 3
            vertexAngles = self.getVertexAngles()
            #TODO Maybe go and make an AngleCloseEnough Function?
            if(abs(0.5*np.pi - vertexAngles[vertexIndex]) < MAX_ANG_DIFF):
                return 1
            elif(abs(0.5*np.pi-vertexAngles[nextVertexIndex]) < MAX_ANG_DIFF):
                return 2
            else:
                return 3

    def getVertexAngles(self):
        vertexAngles = []
        for i in range(len(self.contour)):
            angle = self.getAngleAtVertex(self.contour[i])
            vertexAngles.append(angle)
        return vertexAngles

    #Returns a list of lengths of each side of the given contour.
    def getSideLengths(self):
        sideLengths = []
        for i in range(len(self.contour)):
            length = dist(self.contour[i],
                          self.contour[(i + 1) % len(self.contour)])
            sideLengths.append(length)
        return sideLengths

    #Decides if a contour is a Right angle Isosceles
    def isRightIsosceles(self):
        #Assumes 3 sides.
        #aLen is actual Lengths
        aLen = self.getSideLengths()
        shortest = min(aLen)
        #sLen is scaled Lengths
        sLen = [i / shortest for i in aLen]
        sLen.sort()
        rt2 = math.sqrt(2)
        if sLen[1] - 1.0 < 0.1 and abs(sLen[2] - rt2) < 0.1:
            return True

    #Decides if the given contour is a square.
    def isSquare(self):
        if len(self.contour) != 4:
            return False
        for i in range(4):
            #Pick three corners.
            p1 = (self.contour[i])
            p2 = (self.contour[(i + 1) % 4])
            p3 = (self.contour[(i + 2) % 4])
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

    #Decides if the piece is a parallelogram.
    def isParallelogram(self):
        #Makes the assumptions of 4 sides and not a square.
        aLen = self.getSideLengths()
        for i in range(2):
            d = abs(aLen[i] - aLen[i + 2])
            if d > 0.1 * aLen[i]:
                return False
        return True

    def indentifySymmetry(self, connections):
        """ NOTES
            symmetrySkip is the number of sides to skip when checking different
            configurations. A square has 4 sides and 4 way symmetry so the skip
            number is 1. A parallelogram has 4 sides but 2 way symmetry so the 
            skip number is 2 because 2 shifts need to be made for it to fit.
            This is a bad explanation. TODO: make a picture explanation.
            """
        if self.name == "square":
            self.symmetrySkip = 1
        else:
            self.symmetrySkip = 2

        self.symmetryPattern = self.getSymmetryPattern(connections)

    def getSymmetryPattern(self, connections):
        """How do I get the pieces in a consistent order that represents going
            around in a direction?
            """

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
                if d < MAX_CONNECTION_DIST:
                    connections.append(Connection(pieces[i], other))
    #Remove non-connections from list
    connections = [i for i in connections if i.connectionType != NON_CONNECTION]
    return connections

def indentifySymmetry(pieces, connections):
    for piece in pieces:
        if piece.hasSymmetry:
            piece.indentifySymmetry(connections)

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
        
        cv2.imshow(color, shapeMask)

        ret, thresh = cv2.threshold(shapeMask, 127, 255, 0)
        _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE,
                                         cv2.CHAIN_APPROX_SIMPLE)
        contours = reduceToBlocks(contours)
        for cont in contours:
            valid.append(cont)
    #valid = removeDuplicates(valid)
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

def getColorsByKmeans(img):
    colorCount = 4 # 3 and bg
    height = len(img)
    width = len(img[0])
    pixels = img.reshape((-1,3))
    pixels = np.float32(pixels)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, label, center = cv2.kmeans(pixels, colorCount + 1, None,
                 criteria, 10, flags = cv2.KMEANS_RANDOM_CENTERS)
    colors = []

    for i in range(colorCount+1):
        colors.append( pixels[label.flatten() == i])
    
    

    print center

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