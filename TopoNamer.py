class TopoEdgeAndFaceTracker(object):
    '''A list of  Edges

    The first time an Edge is added, it is considered an 'Open' Edge. The second time, it
    becomes a 'Real' Edge. Any subsequent additions will result in an error
    '''
    def __init__(self):
        # these will each hold a list of all the actual OpenCascade Face and
        # Edge objects that are tracked. If one of these is deleted in an
        # operation, that list item will be changed to None in order to preserve
        # the indices of all the other objects
        self._faces = []
        self._edges = []

        # the keys in these dictionaries will be a static 'name' for each Edge
        # and Face. The user can always use these 'name's to obtain a reference
        # to the Edge/Face they are looking for, regardless of any topologicial
        # changes.

        # values are a dict. the 'edgeIndex' key will hold the index of the Edge
        # in the _edges list. The 'numbShared' key will hold an integer which
        # corresponds to the number of Faces that share this Edge. If any more
        # than 2 Faces share a given Edge, a ValueError will be raised. Only two
        # Faces can share a given Edge in a valid solid
        self._edgeNames = {}
        # values are a dict. the 'faceIndex' key will hold the index of the face
        # in the _faces list. the 'edgeNames' key will hold a list of the
        # names of the Edges that this face has
        self._faceNames = {}

    def _makeName(self, base, sub=False):
        if sub == False:
            if base == 'Face':
                index = len(self._faces) - 1
            elif base == 'Edge':
                index = len(self._edges) - 1
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

    def _addEdge(self, OCCEdge, faceName):
        isAdded = False
        for edgeName in self._edgeNames.keys():
            data    = self._edgeNames[edgeName]
            index   = data['edgeIndex']
            edge    = self._edges[index]
            shared  = data['numbShared']
            if edge.isEqual(OCCEdge):
                if shared == 2:
                    msg = 'Only two faces may share any given Edge in a valid solid'
                    raise ValueError(msg)
                else:
                    self._edgeNames[edgeName]['numbShared'] += 1
                    isAdded = True
                    break
        if isAdded == False:
            self._edges.append(OCCEdge)
            index = len(self._edges) - 1
            edgeName = self._makeName('Edge')
            self._edgeNames[edgeName] = {'numbShared':1,
                                         'edgeIndex':index}
        return edgeName
    
    def _addEdges(self, OCCEdges, faceName):
        names = []
        for edge in OCCEdges:
            name = self._addEdge(edge, faceName)
            names.append(name)
        return names

    def _replaceEdge(self, edgeName, newEdge):
        index = self._edgeNames[edgeName]['edgeIndex']
        self._edges[index] = newEdge

    def addFace(self, OCCFace):
        for i,face in enumerate(self._faces):
            if face.isEqual(OCCFace):
                msg = 'Cannot add the same face more than once.'
                raise ValueError(msg)
        self._faces.append(OCCFace)
        index = len(self._faces) - 1
        faceName = self._makeName('Face')
        names = self._addEdges(OCCFace.Edges, faceName)
        self._faceNames[faceName] = {'faceIndex':index,
                                     'edgeNames':names}
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
