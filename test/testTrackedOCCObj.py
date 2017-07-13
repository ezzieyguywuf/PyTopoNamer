import unittest
from PyTopoNamer.TrackedOCCObj import TrackedOCCObj
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

    def test_getParent(self):
        mock_obj = self.maker.OCCFace()
        trackedObj = TrackedOCCObj(mock_obj, 'Object001', self.trackedOCCObj)
        self.assertEqual(trackedObj.getParent(), self.trackedOCCObj)

    def test_isChildOf(self):
        mock_obj = self.maker.OCCFace()
        trackedObj = TrackedOCCObj(mock_obj, 'Object001', self.trackedOCCObj)
        self.assertTrue(trackedObj.isChildOf(self.trackedOCCObj))

    def test_isNotChildOf(self):
        mock_obj = self.maker.OCCFace()
        mock_obj2 = self.maker.OCCFace()
        trackedObj = TrackedOCCObj(mock_obj, 'Object001')
        trackedObj2 = TrackedOCCObj(mock_obj2, 'Object002', parent=mock_obj)
        self.assertFalse(trackedObj2.isChildOf(self.trackedOCCObj))
