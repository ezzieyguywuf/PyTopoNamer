class TopoEdges(object):
    '''A list of  Edges

    The first time an Edge is added, it is considered an 'Open' Edge. The second time, it
    becomes a 'Real' Edge. Any subsequent additions will result in an error
    '''
    def __init__(self):
        self._seen = {}
        self._openEdges = []
        self._realEdges = {}
        self._lastEdgeNumber = 0

    def append(self, Edge):
        index = None
        for i in range(len(self._openEdges)):
            edge = self._openEdges[i]
            check = edg.isEqual(Edge)
            print('check = {}'.format(check))
            if check:
                self._openEdges.pop(i)
                index = self._lastEdgeNumber
                self._lastEdgeNumber += 1
                self._realEdges[index] = Edge
                break
            elif i == len(self._openEdges) - 1:
                self._openEdges.append(Edge)
            else:
                msg = 'Only two faces may share an Edge'
                raise ValueError(msg)
        return index

    def addEdges(self, Face):
        for edge in Face.Edges:
            self.append(edge)

    def getRealEdges(self):
        return self._edges

    def getOpenEdges(self):
        return [i for i in self._seen.keys() if self._seen[i] is None]

    def getAllEdges(self):
        return [i for i in self._seen.keys()]

class TopoFaces(object):
    def __init__(self):
        self._edges = TopoEdges()
        self._faces = {}
        self._lastFaceNumber = 0

    def newFace(self, Face):
        for index,face in self._faces.items():
            if face.isEqual(Face):
                msg = 'Cannot add two identical Faces. Use `modifyFace` method instead'
                raise ValueError(msg)
        key = self._lastFaceNumber
        self._lastFaceNumber += 1
        self._faces[key] = Face
        self._edges.addEdges(Face)
        return key

class TopoNamer(object):

    """This class manages the topological naming of an OCC Shape object"""

    def __init__(self):
        pass

    def getEdges(self):
        return self._edges.getRealEdges()

    def newFace(self, Face):
        self._faces.addFace(Face)

    def makeBox(self, feature):
        """Track a created box's topology

        :shape: TODO
        :returns: TODO

        """
        shape = feature.Shape
        for face in shape.Faces:
            self.addFace(face)
