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

    def test_updateOCCFace(self):
        mock_face1 = self.maker.OCCFace()

        self.trackedFace.updateOCCFace(mock_face1)
