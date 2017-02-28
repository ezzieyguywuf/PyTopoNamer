import unittest
from unittest import mock
from TopoNamer import TopoNamer, TopoEdgeAndFaceTracker

class FakeOCCEdge(object):
    def isEqual(self):
        pass

class FakeOCCFace(object):
    Edges = list()
    def isEqual(self):
        pass

class FakeOCCShape(object):
    '''A Skeleton class for use in MagicMock's `spec` arguement'''

    Faces = list()

class FakePartFeature(object):

    """A skeleton class for use in MagicMock's `spec` arguement"""

    Shape = FakeOCCShape()

class TestTracker(unittest.TestCase):
    '''Tests the Edges class found in TopoNamer'''
    def setUp(self):
        self.tracker = TopoEdgeAndFaceTracker()

    @staticmethod
    def getMockOCCEdge(side_effect=[False]*10):
        mock_edge = mock.MagicMock(spec=FakeOCCEdge)
        mock_edge.isEqual.side_effect = side_effect
        return mock_edge

    @staticmethod
    def getMockOCCFace(edges=None, isEqual_sideEffect=None):
        mock_face = mock.MagicMock(spec=FakeOCCFace)
        if edges is None:
            edges = []
            for i in range(4):
                edge = TestTracker.getMockOCCEdge()
                edges.append(edge)
        mock_face.Edges = edges

        if isEqual_sideEffect is None:
            isEqual_sideEffect = [False]*10
        mock_face.isEqual.side_effect = isEqual_sideEffect

        return mock_face

    def test_addFace(self):
        mock_face = self.getMockOCCFace()
        check_key = 0
        check_dict = {}
        for i,Edge in enumerate(mock_face.Edges):
            check_dict[i] = check_key

        key = self.tracker.addFace(mock_face)

        self.assertEqual(self.tracker._faces, [mock_face])
        self.assertEqual(key, check_key)
        self.assertEqual(self.tracker._openEdges, check_dict)
        self.assertEqual(self.tracker._edges, mock_face.Edges)

    def test_addTwoFacesWithZeroSharedEdges(self):
        mock_face1 = self.getMockOCCFace()
        mock_face2 = self.getMockOCCFace()

        key1 = self.tracker.addFace(mock_face1)
        key2 = self.tracker.addFace(mock_face2)

        self.assertEqual(self.tracker._faces, [mock_face1, mock_face2])
        self.assertEqual(key1, 0)
        self.assertEqual(key2, 1)
        self.assertEqual(len(self.tracker._openEdges), 8)


        check_dict = {}
        check_edges = []
        for i,Edge in enumerate(mock_face1.Edges + mock_face2.Edges):
            if i <= 3:
                index = 0
            else:
                index = 1
            check_dict[i] = index
            check_edges.append(Edge)
        self.assertEqual(self.tracker._openEdges, check_dict)
        self.assertEqual(self.tracker._edges, check_edges)

    def test_addSameFaceError(self):
        mock_faces = [mock.MagicMock(spec=FakeOCCFace) for i in range(6)]
        for i, mock_face in enumerate(mock_faces):
            if i == 0:
                mock_face.isEqual.side_effect = [False]*4 + [True]
            else:
                mock_face.isEqual.side_effect = [False]*6
        for mock_face in mock_faces[:5]:
            self.tracker.addFace(mock_face)
        self.assertRaises(ValueError, self.tracker.addFace, mock_faces[5])

    def test_addTwoFacesWithSharedEdge(self):
        mock_face1 = self.getMockOCCFace()
        mock_face2 = self.getMockOCCFace()

        sharedEdge = mock_face1.Edges[0]
        mock_face2.Edges[3] = sharedEdge

        index1 = self.tracker.addFace(mock_face1)
        mock_face1.Edges[0].isEqual.side_effect = [True] + [False]*3
        index2 = self.tracker.addFace(mock_face2)

        realEdgeDict = {0:[index1, index2]}
        openEdgeDict = {}
        for i in range(1,7):
            if i <= 3:
                index = index1
            else:
                index = index2
            openEdgeDict[i] = index

        self.assertEqual(self.tracker._realEdges, realEdgeDict)
        self.assertEqual(self.tracker._openEdges, openEdgeDict)

    # def test_getOpenEdges(self):
        # edges = TopoEdges()
        # edges.append(1)
        # edges.append(2)
        # self.assertEqual(edges.getOpenEdges(), [1,2])
        # self.assertEqual(edges.getRealEdges(), [])

    # def test_getRealEdges(self):
        # edges = TopoEdges()
        # edges.append(1)
        # edges.append(1)
        # edges.append(2)
        # self.assertEqual(edges.getOpenEdges(), [2])
        # self.assertEqual(edges.getRealEdges(), [1])

    # def test_getAllEdges(self):
        # edges = TopoEdges()
        # for i in [False, True, False, False, False]:
            # mock_edge = mock.MagicMock(spec=FakeOCCEdge)
            # mock_edge.isEqual
            # edges.append(4)
        # self.assertEqual(edges.getAllEdges(), [1,2,3,4])

    # def test_addEdgeError(self):
        # edges = TopoEdges()
        # occEdge = mock.MagicMock(spec=FakeOCCEdge)
        # occEdge.isEqual.side_effect = [False, False, True]
        # edges.append(occEdge)
        # edges.append(occEdge)
        # self.assertRaises(ValueError, edges.append, occEdge)

class TestFaces(unittest.TestCase):
    '''Tests the Face class defined in TopoNamer'''

    def setUp(self):
        self.faces = TopoFaces()
        self.mock_occFace = mock.MagicMock(spec=FakeOCCFace)

    def test_newFaces(self):
        self.mock_occFace.isEqual.side_effect = [False]*20
        for i in range(6):
            key = self.faces.newFace(self.mock_occFace)
        self.assertEqual(len(self.faces._faces), 6)
        self.assertEqual(key, 5)

class TestNamer(unittest.TestCase):

    """Tests the TopoNamer class"""

    @mock.patch('__main__.FakePartFeature.Shape', new_callable=mock.PropertyMock)
    def setUp(self, mock_shape):
        self._myNamer = TopoNamer()
        self.mock_feature = mock.MagicMock(name='PartFeature', spec_set=FakePartFeature())

    # @mock.patch('TopoNamer.TopoNamer.newFace')
    # def test_makeBox(self, mock_newFace):
        # self.mock_feature.Shape.Faces = range(6)
        # self._myNamer.makeBox(self.mock_feature)
        # self.assertEqual(mock_newFace.call_count, 6)

    def tearDown(self):
        pass

if __name__=='__main__':
    unittest.main()
