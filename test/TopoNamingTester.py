import unittest
from unittest import mock
from PyTopoNamer import TopoNamer, TopoEdgeAndFaceTracker
from TestingHelpers import MockObjectMaker
from TrackedEdge import TrackedEdge

class TestNamer(unittest.TestCase):

    """Tests the TopoNamer class"""

    def getEdge(self, faceName1, faceName2):
        '''Retrieve an Edge based on the two face names'''
        check = [faceName1, faceName2]
        check.sort()
        for edgeName, data in self.myNamer._tracker._edgeNames.items():
            faces = data['faceNames']
            if check == faces:
                print('Returning edge numb {} between faces {}'.format(edgeName, faces))
                return self.myNamer._tracker.getEdge(edgeName)
        msg = 'Edge not found between {}'.format(check)
        raise ValueError(msg)

    def setUp(self):
        self.myNamer = TopoNamer()
        self.maker = MockObjectMaker()

    def test_makeBox(self):
        mock_feature = self.maker.BoxFeature()
        self.myNamer.addShape(mock_feature)
        self.assertEqual(len(self.myNamer._tracker._faceNames), 6)
        self.assertEqual(len(self.myNamer._tracker._edgeNames), 12)

    def test_makeCylinder(self):
        mock_feature = self.maker.CylinderFeature()
        self.myNamer.addShape(mock_feature)
        self.assertEqual(len(self.myNamer._tracker._faceNames), 3)
        self.assertEqual(len(self.myNamer._tracker._edgeNames), 2)

    def test_chamferBoxEdge(self):
        mock_box = self.maker.BoxFeature()
        self.myNamer.addShape(mock_box)
        import pprint
        print("----original edges----")
        pprint.pprint(self.myNamer._tracker._edgeNames)

        chamfer_face = self.maker.OCCFace()

        # the original box will have 4 modified faces, each with one new Edge. This new
        # Edge will come from the chamfer_face
        new_faces = [chamfer_face]
        modified_faces = [['Face{:03d}'.format(i), self.maker.OCCFace()] for i in [0,2,3,4]]

        # front face shares edges with top and bottom as well as existing right and the
        # new face
        modified_faces[0][1].Edges[0] = modified_faces[1][1].Edges[0]
        modified_faces[0][1].Edges[1] = modified_faces[2][1].Edges[0]
        modified_faces[0][1].Edges[2] = self.getEdge('Face000', 'Face005')
        modified_faces[0][1].Edges[3] = chamfer_face.Edges[0]

        # left face shares edges with top and bottom as well as existing back and the new
        # face
        modified_faces[3][1].Edges[0] = modified_faces[1][1].Edges[1]
        modified_faces[3][1].Edges[1] = modified_faces[2][1].Edges[1]
        modified_faces[3][1].Edges[2] = self.getEdge('Face004','Face001')
        modified_faces[3][1].Edges[3] = chamfer_face.Edges[1]

        # top face shares edges with front (above), left (above), existing right, existing
        # back, as well as the new face
        modified_faces[1][1].Edges[2] = self.getEdge('Face002', 'Face005')
        modified_faces[1][1].Edges[3] = self.getEdge('Face002', 'Face001')
        modified_faces[1][1].Edges.append(chamfer_face.Edges[2])

        # bot face shares edges with front (above), left (above), existing right, existing
        # back, as well as the new face
        modified_faces[2][1].Edges[2] = self.getEdge('Face003', 'Face005')
        modified_faces[2][1].Edges[3] = self.getEdge('Face003', 'Face001')
        modified_faces[2][1].Edges.append(chamfer_face.Edges[3])

        self.myNamer.modifyShape(newFaces=new_faces, modifiedFaces=modified_faces)
        # import pdb; pdb.set_trace()
        realEdges = []
        for edgeName, data in self.myNamer._tracker._edgeNames.items():
            faces = data['faceNames']
            if len(faces) == 2:
                realEdges.append(edgeName)
        print('------post modify edges-----')
        pprint.pprint(self.myNamer._tracker._edgeNames)
        self.assertEqual(len(realEdges), 15)

    def test_fuseCylinderAndBoxOfEqualHeight(self):
        # The cylinder will be taller than the box and will be centered vertically along
        # one edge of the box. Therefore, the Fuse will add three Faces and four Edges
        # while eliminating an edge entirely from the original box.

        mock_box = self.maker.BoxFeature()
        self.myNamer.addShape(mock_box)
        # edge values
        all_edges = [i.value for i in [self.myNamer._tracker.getEdge(j) for j in self.myNamer._tracker._edgeNames.keys()]]
        for faceName, data in self.myNamer._tracker._faceNames.items():
            faceShape = data['faceShape']
            edgeVals = [i.value for i in faceShape.Edges]
        all_edges.sort()

        # the Fuse operation results in three new faces, corresponding to the top, bottom,
        # and lateral faces of the Cylinder
        newFaces = [self.maker.OCCFace(edges=[self.maker.OCCEdge()]), # top has one edge
                    self.maker.OCCFace(edges=[self.maker.OCCEdge()]), # bot has one edge
                    # lateral face has six edges. One each it shares with the top and
                    # bottom faces of the cylinder. Then, it has a shared Edge with each
                    # of the Front, Top, Bottom, and Left faces on the box.
                    self.maker.OCCFace(edges=[self.maker.OCCEdge() for i in list(range(6))])
                    ] 
        # Edges 0-3 are the shared Edges with the Box. Edges 4 and 5 are shared with the
        # Top and Bottom face of the cylinder, respectively.
        newFaces[0].Edges[0] = newFaces[2].Edges[4]
        newFaces[1].Edges[0] = newFaces[2].Edges[5]

        # front, top, bot, and left of box are modified
        modifiedFaces = [['Face{:03d}'.format(i), self.maker.OCCFace()] for i in [0,2,3,4]]
        # first set all the edges from the existing edges, since things will change
        # further on
        modifiedFaces[0][1].Edges[2] = self.getEdge('Face000', 'Face005')
        modifiedFaces[1][1].Edges[2] = self.getEdge('Face002', 'Face005')
        modifiedFaces[1][1].Edges[3] = self.getEdge('Face002', 'Face001')
        modifiedFaces[2][1].Edges[2] = self.getEdge('Face003', 'Face005')
        modifiedFaces[2][1].Edges[3] = self.getEdge('Face003', 'Face001')
        modifiedFaces[3][1].Edges[2] = self.getEdge('Face004', 'Face001')
        # these modified faces share Edges with each other or with existing Edges
        # modifiedFront shares edge with modifiedTop, modifiedBottom, existing right
        # (above), and lateral face in newFaces
        modifiedFaces[0][1].Edges[0] = modifiedFaces[1][1].Edges[0]
        modifiedFaces[0][1].Edges[1] = modifiedFaces[2][1].Edges[0]
        modifiedFaces[0][1].Edges[3] = newFaces[2].Edges[0]
        # modifiedTop shares Edge with modifiedFront (above), modifiedLeft, existing right
        # (above), existing back (above), and a new edge which it shares with the lateral
        # face in newfaces
        modifiedFaces[1][1].Edges[1] = modifiedFaces[3][1].Edges[0]
        modifiedFaces[1][1].Edges.append(newFaces[2].Edges[1])
        # modifiedBottom shares edge with modifiedFront (above), modifiedLeft, existing
        # right (above), existing back (above), and a new edge which it shares with the
        # lateral face in newFaces
        modifiedFaces[2][1].Edges[1] = modifiedFaces[3][1].Edges[1]
        modifiedFaces[2][1].Edges.append(newFaces[2].Edges[2])
        # modifiedLeft shares edge with modifiedTop (above), modifiedBottom (above),
        # existing back (above), and the lateral face in newFaces
        modifiedFaces[3][1].Edges[3] = newFaces[2].Edges[3]

        self.myNamer.modifyShape(newFaces, modifiedFaces)
        self.assertEqual(len(self.myNamer._tracker._edgeNames), 16)

    def tearDown(self):
        pass

if __name__=='__main__':
    unittest.main()
