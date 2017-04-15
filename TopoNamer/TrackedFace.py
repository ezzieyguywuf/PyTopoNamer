class TrackedFace(object):
    '''This class will hold instances of a tracked OpenCascade Face object
    
    It will also include enough information to determine whether or not there are other
    tracked faces that have a common OpenCascade Edge with this face'''

    def __init__(self, occFace, name):
        self._occFace = occFace
        self._unsharedEdges = list(range(len(occFace.Edges)))
        self._name = name

    def getOCCFace(self):
        return self._occFace

    def getName(self):
        return self._name

    def _unshareEdge(self, index):
        try:
            toPop = self._unsharedEdges.index(index)
        except ValueError:
            msg = 'No more than two Faces can share a single Edge'
            raise ValueError(msg)
        self._unsharedEdges.pop(toPop)

    def isEdgeShared(self, occEdge):
        for Edge in self._occFace.Edges:
            if Edge.isEqual(occEdge):
                return True
        return False

    def updateUnsharedEdge(self, occEdge):
        for i,Edge in enumerate(self._occFace.Edges):
            if Edge.isEqual(occEdge):
                self._unshareEdge(i)
