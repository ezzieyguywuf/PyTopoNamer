class TopoEdgeAndFaceTracker(object):
    '''A list of  Edges

    The first time an Edge is added, it is considered an 'Open' Edge. The second time, it
    becomes a 'Real' Edge. Any subsequent additions will result in an error
    '''
    def __init__(self):
        self._edgeNames = {}
        self._faceNames = {}

        # This will be the basis for face and edge numbering. Sub-faces and sub-edges will
        # not add to this value.
        self._numbFaces = 0
        self._numbEdges = 0

    def _isNamedEdge(self, Edge):
        for edgeName in self._edgeNames.keys():
            try:
                checkEdge = self.getEdge(edgeName)
            except ValueError:
                return False
            if Edge.isEqual(checkEdge):
                return True
        return False

    def getEdge(self, edgeName):
        face1, face2 = self._edgeNames[edgeName]
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

    def _addEdge(self, faceName1, faceName2):
        '''Add a named tracked Edge.

        This edge is defined by the two faces that have this Edge in common.'''
        faceNames = [faceName1, faceName2]
        edgeName = self._makeName('Edge')
        faceNames.sort()
        self._edgeNames[edgeName] = faceNames

    def _updateEdge(self, Edge1, faceName1):
        '''Check if `Edge1` is present in any 'open' Face.

        If it is, returns True and decrements the appropriate `openfaces` value'''
        for faceName2, data in self._faceNames.items():
            openEdges = data['openEdges']
            if openEdges == 0:
                continue
            face = data['faceShape']
            for Edge2 in face.Edges:
                if Edge1.isEqual(Edge2):
                    check =  self._isNamedEdge(Edge1)
                    if check == True:
                        msg = 'Cannot have more than two Faces share any given Edge'
                        raise ValueError(msg)
                    self._faceNames[faceName2]['openEdges'] -= 1
                    self._addEdge(faceName1, faceName2)
                    return True
        return False

    def addFace(self, OCCFace):
        '''Add an OpenCascade Face object to the tracked Faces list

        This will also check all the OpenCascadeEdges in `OCCFace` against all the Edges
        in the currently 'open' tracked Faces. Any Edges that are present in both
        `OCCFace` and an 'open' tracked Face will be added to the list of tracked named
        Edges'''
        for data in self._faceNames.values():
            face = data['faceShape']
            if face.isEqual(OCCFace):
                msg = 'Cannot add the same face more than once.'
                raise ValueError(msg)
        faceName = self._makeName('Face')
        numbEdges = len(OCCFace.Edges)

        for Edge in OCCFace.Edges:
            match = self._updateEdge(Edge, faceName)
            if match == True:
                numbEdges -= 1

        self._faceNames[faceName] = {'faceShape':OCCFace,
                                     'openEdges':numbEdges}

        return faceName

    def modifyFace(self, oldFaceName, newFaceShape):
        if not oldFaceName in self._faceNames.keys():
            msg = '{} does not exist in the history'.format(oldFaceName)
            raise ValueError(msg)

        numbEdges = len(newFaceShape.Edges)
        self._faceNames[oldFaceName] = {'faceShape':newFaceShape,
                                        'openEdges':numbEdges}
        for Edge in newFaceShape.Edges:
            self._updateEdge(Edge, oldFaceName)

class TopoNamer(object):

    """This class manages the topological naming of an OCC Shape object"""

    def __init__(self):
        self._tracker = TopoEdgeAndFaceTracker()

    def addShape(self, feature):
        """Track a created Shape's topology

        :feature: A FreeCAD PartFeature
        """
        shape = feature.Shape
        for face in shape.Faces:
            self._tracker.addFace(face)

    def modifyShape(self, newFaces=None, modifiedFaces=None, deletedFaces=None):
        if all([i is None for i in [newFaces, modifiedFaces, deletedFaces]]):
            msg = 'At least one of newFaces, modifiedFaces, or deletedFaces must be provided'
            raise ValueError(msg)
        if not newFaces is None:
            for face in newFaces:
                self._tracker.addFace(face)

        if not modifiedFaces is None:
            for oldFace, newFace in modifiedFaces:
                self._tracker.modifyFace(oldFace, newFace)
