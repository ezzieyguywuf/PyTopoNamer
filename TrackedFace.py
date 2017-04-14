class TrackedFace(object):
    '''This class will hold instances of a tracked OpenCascade Face object
    
    It will also include enough information to determine whether or not there are other
    tracked faces that have a common OpenCascade Edge with this face'''

    def __init__(self, occFace, name):
        self._occFace = occFace
        self._unsharedEdges = list(range(len(occFace.Edges)))
        self._name = name

    def isEdgeShared(self, occEdge):
        for Edge in self._occFace.Edges:
            if Edge.isEqual(occEdge):
                return True
        return False
