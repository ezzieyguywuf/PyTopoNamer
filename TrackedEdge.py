class TrackedEdge(object):

    """Tracks a given OpenCascade Edge.
    
    Also keeps track of whether or not this Edge is 'valid'. A 'valid' Edge is one that
    has two faces which share it. If one or both of these Faces no longer exist, the Edge
    is invalid"""

    def __init__(self, occEdge, edgeName):
        self._occEdge = occEdge
        self._name = edgeName
        self._valid = False
        self._faceNames = []

    def _checkEdge(self, occEdge):
        if occEdge.isEqual(self._occEdge):
            return True
        return False

    def _checkEdges(self, occEdges):
        for occEdge in occEdges:
            check = self._checkEdge(occEdge)
            if check:
                return True
        return False

    def addFace(self, trackedFace):
        '''Check if this TrackedEdge has a common Edge with trackedFace
        
        If it does, we will add the name of the face to _faceNames'''

        if self._checkEdges(trackedFace.getOCCFace().Edges):
            self._faceNames.append(trackedFace.getName())
            return True
        return False
