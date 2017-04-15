import unittest
from TopoNamer.TrackedFace import TrackedFace
from test.TestingHelpers import MockObjectMaker

class TestTrackedFace(unittest.TestCase):
    def setUp(self):
        self.maker = MockObjectMaker()
        self.mock_face0 = self.maker.OCCFace()
        self.trackedFace = TrackedFace(self.mock_face0, 'Face000')

    def test_getOCCFace(self):
        fetchedFace = self.trackedFace.getOCCFace()
        self.assertTrue(fetchedFace.isEqual(self.mock_face0))

    def test_getName(self):
        fetchedName = self.trackedFace.getName()
        self.assertEqual(fetchedName, 'Face000')

    def test_createNewTrackedFace(self):
        self.assertEqual(self.mock_face0, self.trackedFace._occFace)
        self.assertEqual('Face000', self.trackedFace._name)
        self.assertEqual([0,1,2,3], self.trackedFace._unsharedEdges)

    def test_isSharedEdgeTrue(self):
        isShared = self.trackedFace.isEdgeShared(self.mock_face0.Edges[0])
        self.assertTrue(isShared)

    def test_isSharedEdgeFalse(self):
        mock_edge0 = self.maker.OCCEdge()

        isShared = self.trackedFace.isEdgeShared(mock_edge0)
        self.assertFalse(isShared)

    def test_updateUnsharedEdge(self):
        self.trackedFace.updateUnsharedEdge(self.mock_face0.Edges[0])
        self.assertEqual(self.trackedFace._unsharedEdges, [1,2,3])

    def test_updateUnsharedEdgeError(self):
        self.trackedFace._unsharedEdges = [1,2,3]

        self.assertRaises(ValueError, self.trackedFace.updateUnsharedEdge, self.mock_face0.Edges[0])

    def test_updateOCCFace(self):
        mock_face1 = self.maker.OCCFace()

        self.trackedFace.updateOCCFace(mock_face1)

        self.assertEqual(self.trackedFace._unshareEdges, [0,1,2,3])
