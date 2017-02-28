import unittest
from unittest import mock
from TopoNamer import TopoNamer, TopoEdges, TopoFaces

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

class TestEdges(unittest.TestCase):
    '''Tests the Edges class found in TopoNamer'''

    def test_addEdge(self):
        edges = TopoEdges()
        mock_Edge = mock.MagicMock(spec=FakeOCCEdge)
        index = edges.append(mock_Edge)
        self.assertEqual(edges.getAllEdges(), [mock_Edge])
        self.assertEqual(index, 0)

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

    def test_newFace(self):
        key = self.faces.newFace(self.mock_occFace)
        self.assertEqual(len(self.faces._faces), 1)
        self.assertEqual(key, 0)

    def test_newFaces(self):
        self.mock_occFace.isEqual.side_effect = [False]*20
        for i in range(6):
            key = self.faces.newFace(self.mock_occFace)
        self.assertEqual(len(self.faces._faces), 6)
        self.assertEqual(key, 5)

    def test_addSameFaceError(self):
        mock_faces = [mock.MagicMock(spec=FakeOCCFace) for i in range(6)]
        for i, mock_face in enumerate(mock_faces):
            if i == 0:
                mock_face.isEqual.side_effect = [False]*4 + [True]
            else:
                mock_face.isEqual.side_effect = [False]*6
        for mock_face in mock_faces[:5]:
            self.faces.newFace(mock_face)
        self.assertRaises(ValueError, self.faces.newFace, mock_faces[5])

    def test_addEdge(self):
        '''Note: an Edge is not added directly. It is added in the background whenever two
        faces that share an Edge are present.'''
        mock_face1 = mock.MagicMock(spec=FakeOCCFace)
        mock_face2 = mock.MagicMock(spec=FakeOCCFace)
        edges = [mock.MagicMock(spec=TopoEdges)]*7

        # Includes edges 0, 1, 2, 3
        mock_face1.Edges = edges[:4]
        # Includes edges 3, 4, 5, 6
        mock_face2.Edges = edges[3:]

        mock_face1.isEqual.side_effect = [False]*6

        self.faces.newFace(mock_face1)
        self.faces.newFace(mock_face2)

        # import pdb; pdb.set_trace()
        self.assertEqual(self.getEdges(), [3])


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
