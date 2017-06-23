from TopoNamer.TrackedFace import TrackedFace
from TopoNamer.TrackedEdge import TrackedEdge

class TopoTracker(object):
    ''' Tracks the topological Faces and Edges of one solid.
    
    This tracking is accomplished by utilizing the helper classes `TrackedFace` and
    `TrackedEdge`. This class keeps a list of `TrackedFace`s and `TrackedEdge`s. These are
    added primarily through the `addFace` method.
    
    Any time a face is added, a new `TrackedFace` instance is created. Next, each edge in
    the recently added face is checked - if there are not currently ane `TrackedEdge`s
    that are topologically equivalent (using OCC's `isEqual` method) to one of the new
    edges, a new `TrackedEdge` is created. Otherwise, the existing `TrackedEdge` is
    updated with the current face, i.e. as a second face that shares the Edge.'''
    def __init__(self):
        self._edgeTrackers = []
        self._faceTrackers = [] 

        # This will be the basis for face and edge numbering. Sub-faces and sub-edges will
        # not add to this value.
        self._numbFaces = 0
        self._numbEdges = 0

    def _isTrackedEdge(self, OCCEdge):
        '''Checks if OCCEdge is already being tracked.
        
        If it is, returns the index of the appropriate tracker in self._edgeTrackers.
        Otherwise, returns None.'''
        for i, edgeTracker in enumerate(self._edgeTrackers):
            trackedOCCEdge = edgeTracker.getOCCEdge()
            if trackedOCCEdge.isEqual(OCCEdge):
                return i
        return None

    def _clearFaceFromEdgeTrackers(self, faceName):
        '''Checks for faceName in self._edgeTrackers. If present, deletes it.'''

        for edgeTracker in self._edgeTrackers:
            if edgeTracker.hasFace(faceName):
                edgeTracker.delFace(faceName)

    def _getFaceTracker(self, OCCFace):
        '''return the `FaceTracker` that is tracking OCCFace
        
        raises exception if OCCFace is not being tracked'''
        for faceTracker in self._faceTrackers:
            if faceTracker.getOCCFace().isEqual(OCCFace):
                return faceTracker
        msg = "That OCCFace is not being tracked"
        raise ValueError(msg)

    def _getEdgeTracker(self, EdgeName):
        '''Return the `EdgeTracker` that is tracking the edge defined by EdgeName

        raises ValueError if the EdgeName has no tracker'''
        #TODO: speed this up - maybe create a dictionary with key-value pairs of
        # EdgeNames-IndexNumber
        for edgeTracker in self._edgeTrackers:
            if EdgeName == edgeTracker.getName():
                return edgeTracker
        msg = '{} is not a valid EdgeName. There is no tracker with that name'
        raise ValueError(msg)

    def getEdgeName(self, OCCEdge):
        index = self._isTrackedEdge(OCCEdge)
        if index is None or not self._edgeTrackers[index].isValid():
            msg = 'This edgeName is invalid - no two Faces share it'
            raise ValueError(msg)
        return self._edgeTrackers[index].getName()

    def getLatestEdge(self, edgeName):
        '''Given edgeName, returns the latest version of this OCCEdge.
        
        This could be multiple Edges if the Edge was split at some point. For that reason,
        this method always returns a list of OCCEdges '''

        edgeTracker = self._getEdgeTracker(edgeName)
        return [edgeTracker.getOCCEdge()]

    def _makeName(self, base, sub=False):
        if sub == False:
            if base == 'Face':
                index = self._numbFaces
                self._numbFaces += 1
            elif base == 'Edge':
                index = self._numbEdges
                self._numbEdges += 1
            else:
                msg = 'Must be either \'Face\' or \'Edge\''
                raise ValueError(msg)
            name = '{}{:03d}'.format(base, index)
        else:
            cur_letter = base[-1]
            if cur_letter.isdigit():
                index = 'a'
            elif cur_letter == 'z':
                base = base[:-1]
                index = 'aa'
            else:
                base = base[:-1]
                index = chr(ord(cur_letter) + 1)
            name = '{}{}'.format(base, index)
        return name

    def addFace(self, OCCFace):
        '''Adds OCCFace to the list of tracked Faces'''
        for face in self._faceTrackers:
            occFace = face.getOCCFace()
            if occFace.isEqual(OCCFace):
                msg = 'A given OpenCascade Face may only be tracked once.'
                raise ValueError(msg)
        name = self._makeName('Face')
        trackedFace = TrackedFace(OCCFace, name)
        self._faceTrackers.append(trackedFace)

        self._checkEdges(trackedFace)

    def _checkEdges(self, trackedFace):
        '''Updates the list of `TrackedEdge`s appropriately.
        
        For each Edge in trackedFace, check if there is already a `TrackedEdge` for it. If
        not, create one. If so, add this `trackedFace` to it.'''
        OCCEdges = trackedFace.getOCCFace().Edges
        for OCCEdge in OCCEdges:
            check = self._isTrackedEdge(OCCEdge)
            if not check is None:
                self._edgeTrackers[check].addFace(trackedFace)
            else:
                edgeName = self._makeName('Edge')
                trackedEdge = TrackedEdge(OCCEdge, edgeName)
                trackedEdge.addFace(trackedFace)
                self._edgeTrackers.append(trackedEdge)

    def modifyFace(self, oldOCCFace, newOCCFace):
        '''Modify the existing `TrackedFace` with the newOCCFace'''
        faceTracker = self._getFaceTracker(oldOCCFace)

        name = faceTracker.getName()
        faceTracker.updateOCCFace(newOCCFace)
        self._clearFaceFromEdgeTrackers(name)
        self._checkEdges(faceTracker)
