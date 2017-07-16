from unittest import mock

class BaseFakeOCCObject(object):
    def __init__(self, value):
        self.value = value

    def isEqual(self, check):
        return check.value == self.value

    def isSame(self, check):
        return self.isEqual(check)

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
        self._boxFaces = {'front':0,
                          'back':1,
                          'top':2,
                          'bottom':3,
                          'left':4,
                          'right':5}

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
        mock_feature = self.FreeCADFeature()

        frt = self._boxFaces['front']
        bck = self._boxFaces['back']
        top = self._boxFaces['top']
        bot = self._boxFaces['bottom']
        lft = self._boxFaces['left']
        rgt = self._boxFaces['right']

        faces = [self.OCCFace() for i in range(6)]

        faces[top].Edges[0] = faces[frt].Edges[0]
        faces[bot].Edges[0] = faces[frt].Edges[1]
        faces[lft].Edges[0] = faces[frt].Edges[2]
        faces[rgt].Edges[0] = faces[frt].Edges[3]

        faces[top].Edges[1] = faces[bck].Edges[0]
        faces[bot].Edges[1] = faces[bck].Edges[1]
        faces[lft].Edges[1] = faces[bck].Edges[2]
        faces[rgt].Edges[1] = faces[bck].Edges[3]

        faces[lft].Edges[2] = faces[top].Edges[2]
        faces[rgt].Edges[2] = faces[top].Edges[3]

        faces[lft].Edges[3] = faces[bot].Edges[2]
        faces[rgt].Edges[3] = faces[bot].Edges[3]

        mock_feature.Shape.Faces = faces
        return mock_feature

    def createFillet(self):
        '''Will create a fillet between the Front and Top faces'''
        # Since OCC rebuilds the entire solid, every single face will need to be updated
        newBox = self.BoxFeature()

        # The fillet is an additional face that is present on the new Box Feature
        filletFace = self.OCCFace()

        # The fillet shares an Edge with four of the box faces. The two faces between
        # which the fillet is made will each have their previously common edge replaced by
        # a new Edge that comes from the Fillet Face
        i1 = self._boxFaces['front']
        i2 = self._boxFaces['top']
        occFace1 = newBox.Shape.Faces[i1]
        occFace2 = newBox.Shape.Faces[i2]

        occFace1.Edges[0] = filletFace.Edges[0]
        occFace2.Edges[0] = filletFace.Edges[1]

        # Finally, the Fillet also shares an Edge with the two Faces that were adjacent to
        # the Faces that had the fillet added. Rather than replacing an existing Edge, the
        # Fillet is an additional (i.e. fifth) Edge to these Faces
        i3 = self._boxFaces['left']
        i4 = self._boxFaces['right']

        occFace3 = newBox.Shape.Faces[i3]
        occFace4 = newBox.Shape.Faces[i4]

        occFace3.Edges.append(filletFace.Edges[2])
        occFace4.Edges.append(filletFace.Edges[3])


        newBox.Shape.Faces[i1] = occFace1
        newBox.Shape.Faces[i2] = occFace2
        newBox.Shape.Faces[i3] = occFace3
        newBox.Shape.Faces[i4] = occFace4

        return filletFace, newBox

    def CylinderFeature(self):
        mock_feature = self.FreeCADFeature()

        edges = [self.OCCEdge() for i in range(3)]
        bot_face = self.OCCFace(edges=[edges[0]])
        top_face = self.OCCFace(edges=[edges[1]])
        lat_face = self.OCCFace(edges=edges)

        mock_feature.Shape.Faces = [bot_face, top_face, lat_face]
        return mock_feature
