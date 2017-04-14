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

    def _addEdge(self, faceName1, faceName2):
        '''Add a named tracked Edge.

        This edge is defined by the two faces that have this Edge in common.'''
        faceNames = [faceName1, faceName2]
        edgeName = self._makeName('Edge')
        faceNames.sort()
        self._edgeNames[edgeName] = {'faceNames':faceNames,
                                     'valid':True}

    def _checkForNewEdges(self, newOCCFace, newFaceName):
        '''For a newly added face, checks each Edge to see if a new namedEdge has been
        created

        A namedEdge is created when two faces have a common Edge.
        '''
        edgeIndices = list(range(len(newOCCFace.Edges)))
        toBlank = []
        # for each Edge in the Face which is being added
        for i, Edge1 in enumerate(newOCCFace.Edges):
            # Check each Face that is currently stored
            for faceName2, faceData in self._faceNames.items():
                # check only the 'open' Edges
                toBlank2 = []
                for j in faceData['openEdgeIndices']:
                    Edge2 = faceData['faceShape'].Edges[j]
                    if Edge1.isEqual(Edge2):
                        toBlank.append(i)
                        toBlank2.append(j)
                        self._addEdge(newFaceName, faceName2)
                orig = self._faceNames[faceName2]['openEdgeIndices']
                newVals = [value for i,value in enumerate(orig) if i not in toBlank2]
                self._faceNames[faceName2]['openEdgeIndices'] = newVals
        edgeIndices = [value for i,value in enumerate(edgeIndices) if i not in toBlank]
        return edgeIndices

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
        edgeIndices = self._checkForNewEdges(OCCFace, faceName)

        self._faceNames[faceName] = {'faceShape':OCCFace,
                                     'openEdgeIndices':edgeIndices}

        return faceName

    def modifyFace(self, oldFaceName, newFaceShape):
        if not oldFaceName in self._faceNames.keys():
            msg = '{} does not exist in the history'.format(oldFaceName)
            raise ValueError(msg)

        # first, remove the old face from our dictionary, so we're not iterating over it
        oldFace = self._faceNames.pop(oldFaceName)

        # replace the old Face data with the new face Data. Don't add it to our dictionary
        # yet
        oldFace['faceShape'] = newFaceShape
        oldFace['openEdges'] = len(newFaceShape.Edges)

        # since we've removed the face, we have to remove all traces of it. This means:
        # 1) if it was part of a self._edgeNames pair, we must remove it from there
        # 2) since we're removing it, we must increment
        for edgeName, faces in self._edgeNames.items():
            if oldFaceName in faces:
                if faces[0] == oldFaceName:
                    which = faces[1]
                else:
                    which = faces[0]
                self._faceNames[which]['openEdges'] += 1

        for Edge in newFaceShape.Edges:
            match = self._updateEdge(Edge, oldFaceName)
            if match == True:
                oldFace['openEdges'] -= 1

        self._faceNames[oldFaceName] = oldFace

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
            for oldFaceName, newFace in modifiedFaces:
                self._tracker.modifyFace(oldFaceName, newFace)
