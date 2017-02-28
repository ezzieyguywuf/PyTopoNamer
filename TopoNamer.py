class TopoEdgeAndFaceTracker(object):
    '''A list of  Edges

    The first time an Edge is added, it is considered an 'Open' Edge. The second time, it
    becomes a 'Real' Edge. Any subsequent additions will result in an error
    '''
    def __init__(self):
        self._seen = {}
        self._faces = []
        self._openEdges = {}
        self._realEdges = {}
        self._lastEdgeNumber = 0

    def getNumbFaces(self):
        return len(self._faces)

    def getAllFaces(self):
        return self._faces

    def addFace(self, OCCFace):
        for face in self._faces:
            if face.isEqual(OCCFace):
                msg = 'Cannot add the same face more than once.'
                raise ValueError(msg)
        self._faces.append(OCCFace)
        index = len(self._faces) - 1
        for Edge in OCCFace.Edges:
            self._addEdge(Edge, index)
        return index

    def _addEdge(self, OCCEdge, faceIndex):
        self._openEdges[OCCEdge] = faceIndex

    def addEdges(self, Face):
        for edge in Face.Edges:
            self.append(edge)

    def getRealEdges(self):
        return self._realEdges

    def getOpenEdges(self):
        return self._openEdges

    def getAllEdges(self):
        return self._openEdges + self._realEdges

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
