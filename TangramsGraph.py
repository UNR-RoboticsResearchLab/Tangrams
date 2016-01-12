import copy
import Tangrams
#################################################
##### TODO BUILD STRESS TESTER FOR EQUALITY #####
#################################################


class TangramsGraph:

    def __init__(self,toCopy = None):
        self.pieces = {}
        self.connections = {}
        if toCopy != None:
            self.pieces = copy.deepcopy(toCopy.pieces)
            self.connections = copy.deepcopy(toCopy.connections)

    def addPiece(self, node):
        self.pieces[node] = []

    def addConnection(self, connection):
        piece1 = connection.pieces[0]
        piece2 = connection.pieces[1]

        #Add connection to connection dict.
        self.connections[connection] = [piece1, piece2]
        #Add each the connection to each piece.
        self.pieces[piece1].append(connection)
        self.pieces[piece2].append(connection)

    def __eq__(self, other):
        return self.countsMatch(other) and self.symmetriesMatch(other) 

    """ countsMatch Description:
        Check to make sure each connection has a match on the other graph that
        has the same types of pieces connected, each connected piece with the
        same number of connections to the correct types.
        """
    def countsMatch(self, other):
        """ NOTES:
            Still fails if a piece is connected with the correct type of
            connection to the correct piece but with the wrong side/point.

            Uses while loops because things are being removed mid loop. Using
            for loops in this scenario leads to wierd stuff.
            """

        #Check to make sure graphs have same number of connections & pieces.
        if(     len(self.connections) != len(other.connections)
            or  len(self.pieces) != len(other.pieces)
           ):
            return False

        #Create copies so items can be removed from the dictionaries as
        #matches are found.
        connections = copy.deepcopy(self.connections)
        otherConnections = copy.deepcopy(other.connections)

        #Loop over all connections of the first graph.
        selfIndex = 0
        while(selfIndex < len(connections)):
            #The current connection in self being paired.
            connection = connections.keys()[selfIndex]

            #Used to break the inner loop if a piece is found.
            pairFound = False

            #Get counts of selfs current connection.
            selfCounts1 = self.getPieceCounts(connection.pieces[0])
            selfCounts2 = self.getPieceCounts(connection.pieces[1])

            otherIndex = 0
            while(otherIndex < len(otherConnections)):

                #The current connection in other being tested for pairing.
                oConnection = otherConnections.keys()[otherIndex]

                #Only proceed if the these are the same type of connection,
                #with the same kinds of pieces.
                if(connection.isSimilar(oConnection)):

                    #Get counts of oConnection.
                    otherCounts1 = other.getPieceCounts(oConnection.pieces[0])
                    otherCounts2 = other.getPieceCounts(oConnection.pieces[1])

                    #If counts match remove the pair from their lists
                    if( self.PieceCountsMatch(selfCounts1, selfCounts2,
                                        otherCounts1, otherCounts2)
                        ):
                        #Match Found remove connections from lists.
                        del connections[connection]
                        del otherConnections[oConnection]
                        otherIndex -= 1
                        selfIndex -= 1

                        #Trip flag to break loop.
                        pairFound = True

                if (pairFound):
                    break

                otherIndex += 1
            #Quit if no pair was found for current piece
            if(not pairFound):
                #print("no pair found for " + str(connection))
                return False

            selfIndex += 1
        #print("First Graph unmatched" + str(connections.keys()))
        #print("Second Graph unmatched" + str(otherConnections.keys()))

        return True

    """ symmetriesMatch Description:
        Returns true if the pieces with symmetries have connections in the
        correct locations.
        """
    def symmetriesMatch(self, other):
        pass

    def PieceCountsMatch(self, counts1, counts2, oCounts1, oCounts2):
        if(counts1 == oCounts1 and counts2 == oCounts2):
            return True
        if(counts1 == oCounts2 and counts2 == oCounts1):
            return True
        return False

    #Returns the number of pieces of each type that it is connected to.
    def getPieceCounts(self, piece):
        return TangramsGraphCounts(self, piece)
    
    def display(self):
        print ("\nConnections")
        self.printConnections()

    def printPieces(self):
        if len(self.pieces) == 0:
            print("No Pieces")
        else:
            for piece in self.pieces:
                connections = self.pieces[piece]
                string = str(piece) + ": "
                for connection in connections:
                    string += str(connection)
                print(string)

    def printConnections(self):
        if len(self.connections) == 0:
            print("No Connections")
        else:
            for connection in self.connections:
                pieces = self.connections[connection]
                string = str(connection)
                print(string)

#Container for the counts of connection and piece type from the given piece.
class TangramsGraphCounts:

    def __init__(self, graph, piece):
        '''NOTES
            'piece in self.pieces' does not return true even if piece is in
            the pieces dict. I think this is from the deepcopy that is done in
            the countsMatch function, but I need that to be able to remove the
            connections from the list without destroying the original data.
            Becuase of the above I've come up with the solution you see below.
        '''
        originalPiece = None
        self.counts = [[0]*3 for i in xrange(3)]
        countIndexes = ["square","triangle","parallelogram"]

        #Weird hacky thing to get the piece from the dictionary into a variable
        for currentPiece in graph.pieces:
            if( str(piece) == str(currentPiece) ):
                originalPiece = currentPiece
                break

        #Shouldn't happen, but just in case.
        if originalPiece == None:
            raise ValueError('The piece is not in the graph dictionary.')


        for connection in graph.pieces[originalPiece]:
            # 1 - the index gives the other index of the list of length 2
            otherPieceIndex = 1 - connection.pieces.index(originalPiece)
            otherPiece = connection.pieces[otherPieceIndex]
            if otherPiece.name in countIndexes:
                countIndex = countIndexes.index(otherPiece.name)
                self.counts[countIndex][connection.connectionType] += 1

    def __eq__(self, other):
        return self.counts == other.counts


### Free Functions ###
def makeGraph(pieces, connections):
    g = TangramsGraph()
    for piece in pieces:
        g.addPiece(piece)
    for connection in connections:
        g.addConnection(connection)
    return copy.deepcopy(g)