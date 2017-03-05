class TopoEdgeAndFaceTracker(object):
    '''A list of  Edges

    The first time an Edge is added, it is considered an 'Open' Edge. The second time, it
    becomes a 'Real' Edge. Any subsequent additions will result in an error
    '''
    def __init__(self):
        self._edgeNames = {}
        self._openFaceNames = {}
        self._closedFaceNames = {}

        # This will be the basis for face and edge numbering. Sub-faces and sub-edges will
        # not add to this value.
        self._numbFaces = 0
        self._numbEdges = 0

    def _getAllFaces(self):
        faces = []
        for data in self._openFaceNames.values():
            faces.append(data['faceShape'])

        for data in self._closedFaceNames.values():
            faces.append(data['faceShape'])

        return faces

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

    def _updateEdge(self, edge):
        for faceName, data in self._openFaceNames.items():
            face = data['faceShape']

    def addFace(self, OCCFace):
        for face in self._getAllFaces():
            if face.isEqual(OCCFace):
                msg = 'Cannot add the same face more than once.'
                raise ValueError(msg)
        faceName = self._makeName('Face')
        numbEdges = len(OCCFace.Edges)
        self._openFaceNames[faceName] = {'faceShape':OCCFace,
                                         'openEdges':numbEdges}
        for Edge in OCCFace.Edges:
            self._updateEdge(Edge)

        return faceName

    def modifyFace(self, oldFaceName, newFaceShape):
        if not oldFaceName in self._faceNames.keys():
            msg = '{} does not exist in the history'.format(oldFaceName)
            raise ValueError(msg)
        faceData = self._faceNames[oldFaceName]
        index = faceData['faceIndex']

        self._faces[index] = newFaceShape
        for i, edgeName in enumerate(faceData['edgeNames']):
            newEdge = newFaceShape.Edges[i]
            self._replaceEdge(edgeName, newEdge)

        edgeNames = self._addEdges(newFaceShape.Edges, oldFaceName)
        self._faceNames[oldFaceName]['edgeNames'] = edgeNames

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
