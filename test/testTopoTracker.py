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

    # def test_addFaceWithSplitSharedEdge(self):
    # NOTE: removed test b/c it is trivial. KEeping in comments just in case.
        # '''face0 and face1 will share two edges.

        # This case is trivial, the two Edges are distinct and new.'''
        # mock_face0 = self.maker.OCCFace() # edges 0, 1, 2 ,3, 4 (see below)
        # mock_face0.Edges.append(self.maker.OCCEdge())
        # mock_face1 = self.maker.OCCFace() # edges 0, 5, 6 ,7, 8 (see below)
        # mock_face1.Edges.append(mock_face0.Edges[-1])
        # mock_face1.Edges[0] = mock_face0.Edges[0]

        # faceName0 = self.tracker.addFace(mock_face0)
        # faceName1 = self.tracker.addFace(mock_face1)

        # # TODO: finish writing this test

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

    def test_getEdgeName(self):
        '''face0 and face1 share one common edge. It should be given a name since it is
        valid'''
        mock_face0 = self.maker.OCCFace() # Edges 0, 1, 2 ,3
        mock_face1 = self.maker.OCCFace() # Edges 0, 5, 6 ,7
        mock_face1.Edges[0] = mock_face0.Edges[0]

        self.tracker.addFace(mock_face0)
        self.tracker.addFace(mock_face1)

        edgeName = self.tracker.getEdgeName(mock_face0.Edges[0])
        self.assertEqual(edgeName, 'Edge000')

    def test_getEdgeName_invalidEdge(self):
        '''face0 and face1 share one common edge. It should be given a name since it is
        valid. Other edges should NOT have a name, since they are invalid'''
        mock_face0 = self.maker.OCCFace() # Edges 0, 1, 2 ,3
        mock_face1 = self.maker.OCCFace() # Edges 0, 5, 6 ,7
        mock_face1.Edges[0] = mock_face0.Edges[0]

        self.tracker.addFace(mock_face0)
        self.tracker.addFace(mock_face1)

        self.assertRaises(ValueError, self.tracker.getEdgeName, mock_face0.Edges[1])

    def test_getEdgeNameFromFaces(self):
        '''If two faces are provided, the name of the Edge they share is returned'''
        mock_face0 = self.maker.OCCFace() # Edges 0, 1, 2 ,3
        mock_face1 = self.maker.OCCFace() # Edges 0, 5, 6 ,7
        mock_face1.Edges[0] = mock_face0.Edges[0]

        faceName0 = self.tracker.addFace(mock_face0)
        faceName1 = self.tracker.addFace(mock_face1)

        edgeName = self.tracker.getEdgeNameFromFaces(faceName0, faceName1)

        self.assertEqual(edgeName, 'Edge000')

    def test_getEdgeByName(self):
        '''should just return the shared edge'''
        mock_face0 = self.maker.OCCFace() # Edges 0, 1, 2 ,3
        mock_face1 = self.maker.OCCFace() # Edges 0, 5, 6 ,7
        mock_face1.Edges[0] = mock_face0.Edges[0]

        self.tracker.addFace(mock_face0)
        self.tracker.addFace(mock_face1)

        edgeName = self.tracker.getEdgeName(mock_face0.Edges[0])
        checkEdge = self.tracker.getEdgeByName(edgeName)
        checkEdgeValues = [edge.value for edge in checkEdge]
        self.assertEqual(checkEdgeValues, [mock_face0.Edges[0].value])

    def test_getEdgeByName_Split(self):
        '''After getting the EdgeName, the Edge becomes split. getEdgeByName should return
        both the split edges'''
        mock_face0a = self.maker.OCCFace() # Edges 0, 1, 2 ,3
        mock_face0b = copy.deepcopy(mock_face0a )# Edges 0, 1, 2 ,3, 4 (see below)
        mock_face0b.Edges.append(self.maker.OCCEdge())
        mock_face1a = self.maker.OCCFace() # Edges 0, 6, 7 ,8
        mock_face1a.Edges[0] = mock_face0a.Edges[0]
        mock_face1b = copy.deepcopy(mock_face1a )# Edges 0, 6, 7, 8, 4 (see below)
        mock_face1b.Edges.append(mock_face0b.Edges[-1])

        self.tracker.addFace(mock_face0a)
        self.tracker.addFace(mock_face1a)
        edgeName = self.tracker.getEdgeName(mock_face0a.Edges[0])

        self.tracker.modifyFace(mock_face0a, mock_face0b)
        self.tracker.modifyFace(mock_face1a, mock_face1b)

        checkEdges = self.tracker.getEdgeByName(edgeName)
        checkValues = [edge.value for edge in checkEdges]

        self.assertEqual(checkValues, [mock_face0b.Edges[0].value, mock_face0b.Edges[-1].value])

    def test_getEdgeByName_InvalidEdge(self):
        '''If an EdgeName is requested that no longer has two faces associated with it, an
        error should be returned'''
        mock_face0 = self.maker.OCCFace() # Edges 0, 1, 2 ,3
        mock_face1a = self.maker.OCCFace() # Edges 0, 6, 7 ,8
        mock_face1b = copy.deepcopy(mock_face1a )# Edges 9, 6, 7, 8
        mock_face1a.Edges[0] = mock_face0.Edges[0]
        mock_face1b.Edges[0] = self.maker.OCCEdge()

        faceName0 = self.tracker.addFace(mock_face0)
        faceName1 = self.tracker.addFace(mock_face1a)
        edgeName = self.tracker.getEdgeNameFromFaces(faceName0, faceName1)
        self.tracker.modifyFace(mock_face1a, mock_face1b)

        self.assertRaises(ValueError, self.tracker.getEdgeByName, edgeName)

    def test_getEdgeByName_Split(self):
        '''After getting the EdgeName, the Edge becomes split. getEdgeByName should return
        both the split edges'''
        mock_face0a = self.maker.OCCFace() # Edges 0, 1, 2 ,3
        mock_face0b = copy.deepcopy(mock_face0a )# Edges 0, 1, 2 ,3, 4 (see below)
        mock_face0b.Edges.append(self.maker.OCCEdge())
        mock_face1a = self.maker.OCCFace() # Edges 0, 6, 7 ,8
        mock_face1a.Edges[0] = mock_face0a.Edges[0]
        mock_face1b = copy.deepcopy(mock_face1a )# Edges 0, 6, 7, 8, 4 (see below)
        mock_face1b.Edges.append(mock_face0b.Edges[-1])

        self.tracker.addFace(mock_face0a)
        self.tracker.addFace(mock_face1a)
        edgeName = self.tracker.getEdgeName(mock_face0a.Edges[0])

        self.tracker.modifyFace(mock_face0a, mock_face0b)
        self.tracker.modifyFace(mock_face1a, mock_face1b)

        checkEdges = self.tracker.getEdgeByName(edgeName)
        checkValues = [edge.value for edge in checkEdges]

        self.assertEqual(checkValues, [mock_face0b.Edges[0].value, mock_face0b.Edges[-1].value])

    def test_getEdgeByName_NewEdge(self):
        '''After getting the EdgeName, the Edge is replaced by a new Edge (maybe the Edge
        got longer). getEdgeByName should return the new Edge'''
        mock_face0a = self.maker.OCCFace() # Edges 0, 1, 2 ,3
        mock_face1a = self.maker.OCCFace() # Edges 0, 5, 6 ,7
        mock_face1a.Edges[0] = mock_face0a.Edges[0]
        mock_face0b = copy.deepcopy(mock_face0a )# Edges 8, 1, 2, 3
        mock_face1b = copy.deepcopy(mock_face1a )# Edges 8, 5, 6, 7
        mock_face0b.Edges[0] = self.maker.OCCEdge()
        mock_face1b.Edges[0] = mock_face0b.Edges[0]

        self.tracker.addFace(mock_face0a)
        self.tracker.addFace(mock_face1a)
        edgeName = self.tracker.getEdgeName(mock_face0a.Edges[0])

        self.tracker.modifyFace(mock_face0a, mock_face0b)
        self.tracker.modifyFace(mock_face1a, mock_face1b)

        checkEdges = self.tracker.getEdgeByName(edgeName)
        checkValues = [edge.value for edge in checkEdges]

        self.assertEqual(checkValues, [mock_face0b.Edges[0].value])
