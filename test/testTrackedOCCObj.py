import unittest
from TopoNamer.TrackedOCCObj import TrackedOCCObj
from test.TestingHelpers import MockObjectMaker

class TestTrackedOCCObj(unittest.TestCase):
    def setUp(self):
        self.maker = MockObjectMaker()
        self.mock_occObj = self.maker.OCCFace()
        self.trackedOCCObj = TrackedOCCObj(self.mock_occObj, 'Object000')

    def test_getOCCFace(self):
        fetchedObj = self.trackedOCCObj.getOCCObj()
        self.assertTrue(fetchedObj.isEqual(self.mock_occObj))

    def test_getName(self):
        fetchedName = self.trackedOCCObj.getName()
        self.assertEqual(fetchedName, 'Object000')

