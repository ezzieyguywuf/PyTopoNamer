from unittest import mock

class BaseFakeOCCObject(object):
    def __init__(self, value):
        self.value = value
    def isEqual(self, check):
        return check.value == self.value

class FakeOCCEdge(BaseFakeOCCObject):
    def __init__(self, value):
        super(FakeOCCEdge, self).__init__(value)

class FakeOCCFace(BaseFakeOCCObject):
    Edges = list()

class FakeOCCShape(object):
    '''A Skeleton class for use in MagicMock's `spec` arguement'''

    Faces = list()

class FakePartFeature(object):

    """A skeleton class for use in MagicMock's `spec` arguement"""

    Shape = FakeOCCShape()

class MockObjectMaker(object):
    def __init__(self):
        self._count = {}

    def _getValue(self, key):
        if not key in self._count.keys():
            self._count[key] = 0
            value = 0
        else:
            self._count[key] += 1
            value = self._count[key]
        return value

    def FreeCADFeature(self):
        mock_feature = mock.MagicMock(spec=FakePartFeature)
        return mock_feature

    def OCCEdge(self, value=None):
        if value is None:
            value = self._getValue('OCCEdge')
        mock_edge = FakeOCCEdge(value)
        return mock_edge

    def OCCFace(self, value=None, edges=None):
        '''Create a mock OpenCascade Face object

        if edges is not None, it must be a list of FakeOCCEdge\'s'''
        if value is None:
            value = self._getValue('OCCFace')

        mock_face = FakeOCCFace(value)

        if edges is None:
            edges = [self.OCCEdge() for i in range(4)]

        mock_face.Edges = edges

        return mock_face

    def BoxFeature(self):
        # Front = Face0
        # Back  = Face1
        # Top   = Face2
        # Bot   = Face3
        # Left  = Face4
        # Right = Face5
        mock_feature = self.FreeCADFeature()

        faces = [self.OCCFace() for i in range(6)]

        faces[0].Edges[0] = faces[2].Edges[0]
        faces[0].Edges[1] = faces[3].Edges[0]
        faces[0].Edges[2] = faces[4].Edges[0]
        faces[0].Edges[3] = faces[5].Edges[0]

        faces[1].Edges[0] = faces[2].Edges[1]
        faces[1].Edges[1] = faces[3].Edges[1]
        faces[1].Edges[2] = faces[4].Edges[1]
        faces[1].Edges[3] = faces[5].Edges[1]

        faces[2].Edges[2] = faces[4].Edges[2]
        faces[2].Edges[3] = faces[5].Edges[2]

        faces[3].Edges[2] = faces[4].Edges[3]
        faces[3].Edges[3] = faces[5].Edges[3]

        mock_feature.Shape.Faces = faces
        return mock_feature

    def CylinderFeature(self):
        mock_feature = self.FreeCADFeature()

        edges = [self.OCCEdge() for i in range(3)]
        bot_face = self.OCCFace(edges=[edges[0]])
        top_face = self.OCCFace(edges=[edges[1]])
        lat_face = self.OCCFace(edges=edges)

        mock_feature.Shape.Faces = [bot_face, top_face, lat_face]
        return mock_feature
