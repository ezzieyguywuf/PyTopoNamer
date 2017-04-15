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

    def isValid(self):
        return self._valid

    def getOCCEdge(self):
        return self._occEdge

    def addFace(self, trackedFace):
        '''Check if this TrackedEdge has a common Edge with trackedFace
        
        If it does, we will add the name of the face to _faceNames'''

        if self._checkEdges(trackedFace.getOCCFace().Edges):
            if len(self._faceNames) == 2:
                msg = 'Only two Faces may share a given Edge.'
                raise ValueError(msg)
            self._faceNames.append(trackedFace.getName())
            if len(self._faceNames) == 2:
                self._valid = True
            return True
        return False

    def delFace(self, faceName):
        index = self._faceNames.index(faceName)
        self._faceNames.pop(index)
        self._valid = False
