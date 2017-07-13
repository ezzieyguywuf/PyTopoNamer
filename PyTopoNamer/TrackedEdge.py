from PyTopoNamer.TrackedOCCObj import TrackedOCCObj

class TrackedEdge(TrackedOCCObj):

    """Tracks a given OpenCascade Edge.
    
    Also keeps track of whether or not this Edge is 'valid'. A 'valid' Edge is one that
    has two faces which share it. If one or both of these Faces no longer exist, the Edge
    is invalid"""

    def __init__(self, occEdge, edgeName, parent=None):
        super(TrackedEdge, self).__init__(occEdge, edgeName, parent)
        self._faceNames = []
        self._lastValidFaceNames = []

    def _checkEdges(self, occEdges):
        for occEdge in occEdges:
            if occEdge.isSame(self._occObj):
                return True
        return False

    def getOCCEdge(self):
        '''Convenience method'''
        return self.getOCCObj()

    def hasFace(self, faceName):
        if type(faceName) == type(''):
            return faceName in self._faceNames
        else:
            msg = 'faceName must be the actual topological name of the Face you are checking for'
            raise ValueError(msg)

    def isValid(self):
        '''Returns True if the Edge has two faces that share it.'''
        return len(self._faceNames) == 2

    def addFace(self, trackedFace):
        '''Check if this TrackedEdge has a common Edge with trackedFace
        
        If it does, we will add the name of the face to _faceNames. If it doesn't, then it
        returns false and changes nothing internally '''

        if not self._checkEdges(trackedFace.getOCCFace().Edges):
            msg = 'Cannot add a face that does not contain this Edge'
            raise ValueError(msg)
        elif len(self._faceNames) == 2:
            msg = 'Only two Faces may share a given Edge.'
            raise ValueError(msg)

        self._faceNames.append(trackedFace.getName())
        if len(self._faceNames) == 2:
            self._lastValidFaceNames = self._faceNames[:]


    def delFace(self, faceName):
        index = self._faceNames.index(faceName)
        self._faceNames.pop(index)

    def getFaceNames(self):
        return self._faceNames[:]

    def getLastValidFaceNames(self):
        return self._lastValidFaceNames[:]
