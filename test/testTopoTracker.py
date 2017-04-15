import unittest
from TopoNamer.TopoTracker import TopoTracker
from test.TestingHelpers import MockObjectMaker
import copy

class TestTracker(unittest.TestCase):
    def setUp(self):
        self.maker = MockObjectMaker()
        self.tracker = TopoTracker()

    def test_makeName(self):
        self.tracker._numbFaces = 0
        self.tracker._numbEdges = 2
        name0 = self.tracker._makeName('Face')
        name1 = self.tracker._makeName('Edge')

        self.assertEqual(name0, 'Face000')
        self.assertEqual(name1, 'Edge002')
        name1 = self.tracker._makeName('Edge')
        self.assertEqual(name1, 'Edge003')

    def test_makeSubName(self):
        name0 = self.tracker._makeName('Face001', sub=True)
        name1 = self.tracker._makeName('Edge002bb', sub=True)
        name2 = self.tracker._makeName('Face001az', sub=True)
        name3 = self.tracker._makeName('Edge002z', sub=True)

        self.assertEqual(name0, 'Face001a')
        self.assertEqual(name1, 'Edge002bc')
        self.assertEqual(name2, 'Face001aaa')
        self.assertEqual(name3, 'Edge002aa')

    def test_addTwoFaces_noSharedEdges(self):
        mock_face0 = self.maker.OCCFace()
        mock_face1 = self.maker.OCCFace()

        self.tracker.addFace(mock_face0)
        self.tracker.addFace(mock_face1)

        self.assertTrue(len(self.tracker._faceTrackers) == 2)
        self.assertEqual(len(self.tracker._edgeTrackers), 8)
        for edgeTracker in self.tracker._edgeTrackers:
            self.assertFalse(edgeTracker.isValid())

    def test_addSameFaceError(self):
        mock_face0 = self.maker.OCCFace()

        self.tracker.addFace(mock_face0)

        self.assertRaises(ValueError, self.tracker.addFace, mock_face0)

    def test_addFaceWithSharedEdge(self):
        mock_face0 = self.maker.OCCFace()
        mock_face1 = self.maker.OCCFace()
        mock_face1.Edges[0] = mock_face0.Edges[0]

        self.tracker.addFace(mock_face0)
        self.tracker.addFace(mock_face1)

        self.assertTrue(len(self.tracker._faceTrackers) == 2)
        self.assertEqual(len(self.tracker._edgeTrackers), 7)
        self.assertTrue(self.tracker._edgeTrackers[0].isValid())

    def test_modifyFace_makeEdgeInvalid(self):
        mock_face0 = self.maker.OCCFace()
        mock_face1a = self.maker.OCCFace()
        mock_face1b = copy.deepcopy(mock_face1a)
        mock_face1a.Edges[0] = mock_face0.Edges[0]

        self.tracker.addFace(mock_face0)
        self.tracker.addFace(mock_face1a)
        self.tracker.modifyFace(mock_face1a, mock_face1b)

        self.assertFalse(self.tracker._edgeTrackers[0].isValid())

    def test_modifyFace_edgeStillValid(self):
        mock_face0 = self.maker.OCCFace()
        mock_face1a = self.maker.OCCFace()
        mock_face1b = copy.deepcopy(mock_face1a)
        mock_face1a.Edges[0] = mock_face0.Edges[0]
        mock_face1b.Edges[1] = mock_face0.Edges[0]

        self.tracker.addFace(mock_face0)
        self.tracker.addFace(mock_face1a)
        self.tracker.modifyFace(mock_face1a, mock_face1b)

        self.assertTrue(self.tracker._edgeTrackers[0].isValid())
