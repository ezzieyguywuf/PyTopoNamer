class TrackedEdge(object):

    """Tracks a given OpenCascade Edge.
    
    Also keeps track of whether or not this Edge is 'valid'. A 'valid' Edge is one that
    has two faces which share it. If one or both of these Faces no longer exist, the Edge
    is invalid"""

    def __init__(self, occEdge, edgeName, parent=None):
        self._occEdge = occEdge
        self._name = edgeName
        self._faceNames = []
        self._parent = parent

    def _checkEdges(self, occEdges):
        for occEdge in occEdges:
            if occEdge.isEqual(self._occEdge):
                return True
        return False

    def hasFace(self, faceName):
        return faceName in self._faceNames

    def isValid(self):
        return len(self._faceNames) == 2

    def getOCCEdge(self):
        return self._occEdge

    def getName(self):
        return self._name

    def addFace(self, trackedFace):
        '''Check if this TrackedEdge has a common Edge with trackedFace
        
        If it does, we will add the name of the face to _faceNames'''

        if self._checkEdges(trackedFace.getOCCFace().Edges):
            if len(self._faceNames) == 2:
                msg = 'Only two Faces may share a given Edge.'
                raise ValueError(msg)
            self._faceNames.append(trackedFace.getName())
            return True
        return False

    def delFace(self, faceName):
        index = self._faceNames.index(faceName)
        self._faceNames.pop(index)
