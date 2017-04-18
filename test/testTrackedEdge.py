import unittest
from TopoNamer.TrackedFace import TrackedFace
from TopoNamer.TrackedEdge import TrackedEdge
from test.TestingHelpers import MockObjectMaker

class TestTrackedEdge(unittest.TestCase):

    """Tests the TrackedEdge object"""
    def setUp(self):
        self.maker = MockObjectMaker()
        self.mock_Edge0 = self.maker.OCCEdge()
        mock_Face0 = self.maker.OCCFace()
        self.trackedFace = TrackedFace(mock_Face0, 'Face000')
        self.trackedEdge = TrackedEdge(self.mock_Edge0, 'Edge000')

    def test_getOCCEdge(self):
        fetchedEdge = self.trackedEdge.getOCCEdge()
        self.assertTrue(fetchedEdge.isEqual(self.mock_Edge0))

    def test_createNewTrackedEdge(self):
        self.trackedEdge._name = 'Edge000'
        self.trackedEdge._valid = False

    def test_addFace_noSharedEdge(self):
        retval = self.trackedEdge.addFace(self.trackedFace)

        self.assertFalse(retval)
        self.assertEqual(self.trackedEdge._faceNames, [])

    def test_addFace_yesSharedEdgeFirstFace(self):
        self.trackedFace._occObj.Edges[0] = self.mock_Edge0
        retval = self.trackedEdge.addFace(self.trackedFace)

        self.assertTrue(retval)
        self.assertEqual(self.trackedEdge._faceNames, ['Face000'])

    def test_addFace_yesSharedEdgeSecondFace(self):
        self.trackedFace._occObj.Edges[0] = self.mock_Edge0
        mock_face1 = self.maker.OCCFace()
        mock_face1.Edges[1] = self.mock_Edge0
        trackedFace1 = TrackedFace(mock_face1, 'Face001')

        retval0 = self.trackedEdge.addFace(self.trackedFace)
        retval1 = self.trackedEdge.addFace(trackedFace1)

        self.assertTrue(retval0)
        self.assertTrue(retval1)
        self.assertEqual(self.trackedEdge._faceNames, ['Face000', 'Face001'])

    def test_addFace_errorIfThirdFaceAdded(self):
        self.trackedFace._occObj.Edges[0] = self.mock_Edge0
        mock_face1 = self.maker.OCCFace()
        mock_face1.Edges[1] = self.mock_Edge0
        trackedFace1 = TrackedFace(mock_face1, 'Face001')
        mock_face2 = self.maker.OCCFace()
        mock_face2.Edges[2] = self.mock_Edge0
        trackedFace2 = TrackedFace(mock_face2, 'Face002')

        retval = self.trackedEdge.addFace(self.trackedFace)
        retval = self.trackedEdge.addFace(trackedFace1)

        self.assertTrue(retval)
        self.assertEqual(self.trackedEdge._faceNames, ['Face000', 'Face001'])
        self.assertRaises(ValueError, self.trackedEdge.addFace, trackedFace2)

    def test_isValid_false(self):
        self.trackedEdge.addFace(self.trackedFace)

        self.assertFalse(self.trackedEdge.isValid())

    def test_isValid_true(self):
        self.trackedFace._occObj.Edges[0] = self.mock_Edge0
        mock_face1 = self.maker.OCCFace()
        mock_face1.Edges[1] = self.mock_Edge0
        trackedFace1 = TrackedFace(mock_face1, 'Face001')

        self.trackedEdge.addFace(self.trackedFace)
        self.trackedEdge.addFace(trackedFace1)

        self.assertTrue(self.trackedEdge.isValid())

    def test_delFace(self):
        self.trackedFace._occObj.Edges[0] = self.mock_Edge0
        self.trackedEdge.addFace(self.trackedFace)
        self.trackedEdge.delFace(self.trackedFace.getName())

        self.assertTrue(len(self.trackedEdge._faceNames) == 0)
