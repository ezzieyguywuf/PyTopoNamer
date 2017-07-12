import unittest
from TopoNamer.TopoNamer import TopoNamer
from test.TestingHelpers import MockObjectMaker

class TestTopoNamer(unittest.TestCase):
    def setUp(self):
        self.maker = MockObjectMaker()
        self.namer = TopoNamer()
        self.box = self.maker.BoxFeature()
        self.namer.addShape(self.box)

    # def test_trackShape(self):
        # self.namer.addShape(self.box)
        # self.assertEqual(len(self.namer._tracker._faceTrackers), 6)
        # self.assertEqual(len(self.namer._tracker._edgeTrackers), 12)

    def test_makeFillet(self):
        '''When a fillet is created on an Edge, that Edge is no longer valid.
        
        Also, the FilletFace must '''

        # First, the user selects an Edge visually. This is an OCCEdge
        filletEdge = self.box.Shape.Faces[0].Edges[0]
        filletEdgeName = self.namer._tracker.getEdgeName(filletEdge)

        # Next the user performs the fillet operation. After the fillet is complete, the
        # user must provide a list of modified/created/deleted faces
        filletFace, newBox = self.maker.createFillet()
        for faceIndex in self.maker._boxFaces.values():
            oldFace = self.box.Shape.Faces[faceIndex]
            newFace = newBox.Shape.Faces[faceIndex]
            self.namer._tracker.modifyFace(oldFace, newFace)

        self.namer._tracker.addFace(filletFace)

        self.assertRaises(ValueError, self.namer._tracker.getEdgeByName, filletEdgeName)
