class TopoEdgeAndFaceTracker(object):
    '''A list of  Edges

    The first time an Edge is added, it is considered an 'Open' Edge. The second time, it
    becomes a 'Real' Edge. Any subsequent additions will result in an error
    '''
    def __init__(self):
        self._faces = []
        self._edges = []
        # Each of these dictionaries will use an integer as a key. That integer
        # will correspond to an index in the `self._edges` list, which itself
        # holds a list of OpenCascade Edge objects

        # Each key holds a single integer value, which corresponds to an index
        # in the self._faces list
        self._openEdges = {}
        # Each key holds a pair of integer values, which correspond to indices
        # in the self._faces list. These two faces together comprise the 'real
        # edge'
        self._realEdges = {}

    def addFace(self, OCCFace):
        for face in self._faces:
            check = face.isEqual(OCCFace)
            if check:
                msg = 'Cannot add the same face more than once.'
                raise ValueError(msg)
        self._faces.append(OCCFace)
        index = len(self._faces) - 1
        for Edge in OCCFace.Edges:
            self._addEdge(Edge, index)
        return index

    def _addEdge(self, OCCEdge, faceIndex):
        popped = False
        for i in self._openEdges.keys():
            edge = self._edges[i]
            if edge.isEqual(OCCEdge):
                face1Index = self._openEdges.pop(i)
                self._realEdges[i] = [face1Index, faceIndex]
                popped = True
                break
        if popped == False:
            self._edges.append(OCCEdge)
            index = len(self._edges) - 1
            self._openEdges[index] = faceIndex

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
