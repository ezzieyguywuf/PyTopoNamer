from TopoNamer.TrackedFace import TrackedFace
from TopoNamer.TrackedEdge import TrackedEdge

class TopoTracker(object):
    def __init__(self):
        self._edgeTrackers = []
        self._faceTrackers = [] 

        # This will be the basis for face and edge numbering. Sub-faces and sub-edges will
        # not add to this value.
        self._numbFaces = 0
        self._numbEdges = 0

    def _isNamedEdge(self, Edge):
        for edgeName in self._edgeNames.keys():
            try:
                checkEdge = self.getEdge(edgeName)
            except (KeyError, ValueError):
                return False
            else:
                if Edge.isEqual(checkEdge):
                    return True
        return False

    def getEdge(self, edgeName):
        face1, face2 = self._edgeNames[edgeName]['faceNames']
        face1 = self._faceNames[face1]['faceShape']
        face2 = self._faceNames[face2]['faceShape']

        for edge1 in face1.Edges:
            for edge2 in face2.Edges:
                if edge1.isEqual(edge2):
                    return edge1
        msg = 'This edgeName is invalid - no two Faces share it'
        raise ValueError(msg)

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
        name = self._makeName('Face')
        trackedFace = TrackedFace(OCCFace, name)
        self._faceTrackers.append(trackedFace)
