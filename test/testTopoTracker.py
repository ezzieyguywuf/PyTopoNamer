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

    def test_modifyFaceWithMovedEdge(self):
        # Two faces, face0 and face1a will share one common edge. Next, face1a will be
        # updated to face1b. Instead of face1 sharing its first edge with face0, it will
        # now share its second edge. The overall effect should be that an extra
        # TrackedEdge is generated
        mock_face0 = self.maker.OCCFace() # Edges 0, 1, 2, 3
        mock_face1a = self.maker.OCCFace()# Edges 0, 5, 6, 7 (see below)
        mock_face1b = copy.deepcopy(mock_face1a) # Edges 4, 0, 6, 7 (see below)
        sharedEdge = mock_face0.Edges[0]
        mock_face1a.Edges[0] = sharedEdge
        mock_face1b.Edges[1] = sharedEdge

        self.tracker.addFace(mock_face0)
        self.tracker.addFace(mock_face1a)
        self.tracker.modifyFace(mock_face1a, mock_face1b)

        recoveredEdge = self.tracker._edgeTrackers[0].getOCCEdge()
        recoveredFace = self.tracker._faceTrackers[1].getOCCFace()

        # After the modification, Edges 5,6, and 7 are still being tracked from face1a.
        # However, we must add Edge 4 from face1b. Edge 0 is tracked from face0, thus we
        # don't need to include it from face1a
        checkEdges = mock_face0.Edges + mock_face1a.Edges[1:] + [mock_face1b.Edges[0]]
        checkEdgeValues = [edgeTracker.getOCCEdge().value for edgeTracker in self.tracker._edgeTrackers]
        edgeValues = [i.value for i in checkEdges]
        checkValidEdges = [edgeTracker.isValid() for edgeTracker in self.tracker._edgeTrackers]
        validEdges = [False] * len(self.tracker._edgeTrackers)
        validEdges[0] = True

        self.assertEqual(checkValidEdges, validEdges)
        self.assertEqual(checkEdgeValues, edgeValues)

    def test_modifyFaceWithNoSameEdges(self):
        '''mock_face0 and mock_face1a share a common edge. When mock_face1a is modified to
        mock_face1b, it will no longer share an edge with mock_face0.'''
        mock_face0 = self.maker.OCCFace() # Edges 0, 1, 2 ,3
        mock_face1a = self.maker.OCCFace()# Edges 0, 5, 6, 7 (see below)
        mock_face1a.Edges[0] = mock_face0.Edges[0]
        mock_face1b = self.maker.OCCFace()# Edges 8, 9, 10, 11

        self.tracker.addFace(mock_face0)
        self.tracker.addFace(mock_face1a)
        self.tracker.modifyFace(mock_face1a, mock_face1b)

        trackedEdgesValues = []
        for edgeTracker in self.tracker._edgeTrackers:
            trackedEdgesValues.append(edgeTracker.getOCCEdge().value)

        checkEdges = mock_face0.Edges + mock_face1a.Edges[1:]+ mock_face1b.Edges
        checkEdgesValues = [i.value for i in checkEdges]
        checkValidEdges = [edgeTracker.isValid() for edgeTracker in self.tracker._edgeTrackers]
        validEdges = [False] * len(self.tracker._edgeTrackers)
        # self.assertEqual(checkEdgesValues, trackedEdgesValues)
        self.assertEqual(checkValidEdges, validEdges)
        self.assertEqual(len(self.tracker._edgeTrackers), 11)
