import unittest
from PyTopoNamer.TrackedFace import TrackedFace
from test.TestingHelpers import MockObjectMaker

class TestTrackedFace(unittest.TestCase):
    def setUp(self):
        self.maker = MockObjectMaker()
        self.mock_face0 = self.maker.OCCFace()
        self.trackedFace = TrackedFace(self.mock_face0, 'Face000')

    def test_createNewTrackedFace(self):
        self.assertEqual(self.mock_face0, self.trackedFace._occObj)
        self.assertEqual('Face000', self.trackedFace._name)

    def test_updateOCCFace(self):
        mock_face1 = self.maker.OCCFace()

        self.trackedFace.updateOCCFace(mock_face1)
