import unittest
from PyTopoNamer.TopoNamer import TopoNamer
from test.TestingHelpers import MockObjectMaker

class TestTopoNamer(unittest.TestCase):
    def setUp(self):
        # MockObjectMaker makes mock objects
        self.maker = MockObjectMaker()
        # TopoNamer is the topological tracker/namer
        self.namer = TopoNamer()
        # Let's pretend someone made a box
        self.box = self.maker.BoxFeature()
        # This is how we track the topology of the box
        self.namer.addShape(self.box)

    def test_makeFillet(self):
        '''When a fillet is created on an Edge, that Edge is no longer valid.
        '''

        # First, the user selects an Edge visually. FreeCAD provides this filletEdge
        # directly by way of the visual interface. For the purposes of this test I am
        # grabbing it explicitly from a mock object
        filletEdge = self.box.Shape.Faces[0].Edges[0]

        # The EdgeName is a simple string that can be stored and used later to retrieve
        # the same Edge. The Edge is defined by the two faces that make it up.
        filletEdgeName = self.namer.getEdgeName(filletEdge)

        # Next the user performs the fillet operation.
        filletFace, newBox = self.maker.createFillet()

        # After the fillet is complete, the user must provide a list of
        # modified/created/deleted faces. Note: OpenCascade classes have  methods that
        # should allow us to build these lists easily.
        modifiedFaces  = []
        for faceIndex in self.maker._boxFaces.values():
            oldFace = self.box.Shape.Faces[faceIndex]
            newFace = newBox.Shape.Faces[faceIndex]
            modifiedFaces.append((oldFace, newFace))

        newFaces = [filletFace]

        self.namer.modifyShape(modifiedFaces=modifiedFaces, newFaces=newFaces)

        self.assertRaises(ValueError, self.namer._tracker.getEdgeByName, filletEdgeName)
