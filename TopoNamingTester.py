import unittest
from unittest import mock
from TopoNamer import TopoNamer, TopoEdgeAndFaceTracker
from TestingHelpers import MockObjectMaker


class TestTracker(unittest.TestCase):
    '''Tests the Edges class found in TopoNamer'''
    def setUp(self):
        self.maker = MockObjectMaker()
        self.tracker = TopoEdgeAndFaceTracker()

    def test_addEdge(self):
        mock_edge = self.maker.OCCEdge()

        name = self.tracker._addEdge(mock_edge, 'Face0')

        check_dict = {'Edge0':{'numbShared':1,
                               'edgeIndex':0}}
        self.assertEqual(self.tracker._edges, [mock_edge])
        self.assertEqual(self.tracker._edgeNames, check_dict)
        self.assertEqual(name, 'Edge0')

    def test_addEdgeTwice(self):
        mock_edge = self.maker.OCCEdge()

        name0 = self.tracker._addEdge(mock_edge, 'Face0')
        name1 = self.tracker._addEdge(mock_edge, 'Face1')

        check_dict = {'Edge0':{'numbShared':2,
                               'edgeIndex':0}}
        self.assertEqual(self.tracker._edges, [mock_edge])
        self.assertEqual(self.tracker._edgeNames, check_dict)
        self.assertEqual(name0, 'Edge0')
        self.assertEqual(name1, 'Edge0')

    def test_addEdgeThrice(self):
        mock_edge = self.maker.OCCEdge()

        self.tracker._addEdge(mock_edge, 'Face0')
        self.tracker._addEdge(mock_edge, 'Face1')
        self.assertRaises(ValueError, self.tracker._addEdge, mock_edge, 'Face2')

    def test_addEdges(self):
        edges = [self.maker.OCCEdge() for i in range(10)]

        names = self.tracker._addEdges(edges, 'Face0')
        self.assertEqual(names, ['Edge{}'.format(i) for i in range(10)])


    def test_addFace(self):
        mock_face = self.maker.OCCFace()
        check_name = 'Face0'
        check_dict = {check_name:{'faceIndex':0,
                                  'edgeNames':['Edge{}'.format(i) for i in range(4)]}}

        facename = self.tracker.addFace(mock_face)

        self.assertEqual(self.tracker._faces, [mock_face])
        self.assertEqual(facename, check_name)
        self.assertEqual(self.tracker._faceNames, check_dict)

    def test_addSameFaceError(self):
        mock_faces = [self.maker.OCCFace() for i in range(6)]
        mock_faces[5].value = mock_faces[0].value
        for mock_face in mock_faces[:5]:
            self.tracker.addFace(mock_face)
        self.assertRaises(ValueError, self.tracker.addFace, mock_faces[5])

    def test_addTwoFacesWithZeroSharedEdges(self):
        mock_face1  = self.maker.OCCFace()
        mock_face2  = self.maker.OCCFace()
        check_name0 = 'Face0'
        check_name1 = 'Face1'
        check_dict  = {check_name0:{'faceIndex':0,
                                    'edgeNames':['Edge{}'.format(i) for i in range(4)]},
                       check_name1:{'faceIndex':1,
                                    'edgeNames':['Edge{}'.format(i) for i in range(4,8)]}}

        name0 = self.tracker.addFace(mock_face1)
        name1 = self.tracker.addFace(mock_face2)

        self.assertEqual(self.tracker._faces, [mock_face1, mock_face2])
        self.assertEqual(name0, check_name0)
        self.assertEqual(name1, check_name1)
        self.assertEqual(self.tracker._faceNames, check_dict)

    def test_addTwoFacesWithSharedEdge(self):
        mock_face1 = self.maker.OCCFace()
        mock_face2 = self.maker.OCCFace()
        check_dict  = {'Face0':{'faceIndex':0,
                                'edgeIndices':[0,1,2,3]},
                       'Face1':{'faceIndex':1,
                                'edgeIndices':[4,0,5,6]}}

        mock_face2.Edges[1].value = mock_face1.Edges[0].value

        name1 = self.tracker.addFace(mock_face1)
        name2 = self.tracker.addFace(mock_face2)

        self.assertEqual(self.tracker._faceNames, check_dict)

    def test_addThreeFacesWithSeparateSharedEdges(self):
        mock_face1 = self.maker.OCCFace()
        mock_face2 = self.maker.OCCFace()
        mock_face3 = self.maker.OCCFace()
        check_dict  = {'Face0':{'faceIndex':0,
                                'edgeIndices':[0,1,2,3]},
                       'Face1':{'faceIndex':1,
                                'edgeIndices':[4,0,5,6]},
                       'Face2':{'faceIndex':2,
                                'edgeIndices':[7,8,1,9]}}

        mock_face2.Edges[1].value = mock_face1.Edges[0].value
        mock_face3.Edges[2].value = mock_face1.Edges[1].value

        name1 = self.tracker.addFace(mock_face1)
        name2 = self.tracker.addFace(mock_face2)
        name3 = self.tracker.addFace(mock_face3)

        self.assertEqual(self.tracker._faceNames, check_dict)

    def test_addThreeFacesWithSharedEdgeError(self):
        mock_face1 = self.maker.OCCFace()
        mock_face2 = self.maker.OCCFace()
        mock_face3 = self.maker.OCCFace()

        sharedEdgeValue = mock_face1.Edges[0].value
        mock_face2.Edges[2].value = sharedEdgeValue
        mock_face3.Edges[3].value = sharedEdgeValue

        index1 = self.tracker.addFace(mock_face1)
        index2 = self.tracker.addFace(mock_face2)

        self.assertRaises(ValueError, self.tracker.addFace, mock_face3)

    def test_ModifyFace(self):
        mock_face0 = self.maker.OCCFace()
        mock_face1 = self.maker.OCCFace()
        mock_face2a = self.maker.OCCFace()
        mock_face2b = self.maker.OCCFace()
        check_dict  = {'Face0':{'faceIndex':0,
                                'edgeIndices':[0,1,2,3]},
                       'Face1':{'faceIndex':1,
                                'edgeIndices':[0,4,5,6]},
                       'Face2':{'faceIndex':2,
                                'edgeIndices':[1,7,8,9]}}

        mock_face1.Edges[0].value = mock_face0.Edges[0].value
        mock_face2a.Edges[0].value = mock_face0.Edges[1].value
        mock_face2b.Edges[0].value = mock_face1.Edges[1].value

        self.tracker.addFace(mock_face0) # Edges 0 - 3
        self.tracker.addFace(mock_face1) # Edges 4 - 6 (one shared Edge)
        facename = self.tracker.addFace(mock_face2a) # Edges 7 - 9 (one shared Edge)

        self.tracker.modifyFace(facename, mock_face2b)

        self.assertEqual(self.tracker._faceNames, check_dict)

class TestNamer(unittest.TestCase):

    """Tests the TopoNamer class"""

    def setUp(self):
        self._myNamer = TopoNamer()
        self.maker = MockObjectMaker()

    def test_makeBox(self):
        mock_feature = self.maker.BoxFeature()
        self._myNamer.addShape(mock_feature)
        self.assertEqual(len(self._myNamer._tracker._faces), 6)
        self.assertEqual(len(self._myNamer._tracker._realEdges), 12)

    def test_makeCylinder(self):
        mock_feature = self.maker.CylinderFeature()
        self._myNamer.addShape(mock_feature)
        self.assertEqual(len(self._myNamer._tracker._faces), 3)
        self.assertEqual(len(self._myNamer._tracker._realEdges), 2)

    def test_fuseCylinderAndBoxOfEqualHeight(self):
        mock_box = self.maker.BoxFeature()
        mock_cyl = self.maker.CylinderFeature()

        # cylindrical face is new
        newFaces = [self.maker.OCCFace()]
        # top, bottom, front, and left of box are modified
        modifiedFaces = [(mock_box.Shape.Faces[i], self.maker.OCCFace()) for i in range(4)]
        # The cylindrical lateral face shares an edge with the front and left
        # faces of the box. These are new edges for the cylinder, as it will
        # still retain its seam edge.
        mock_cyl.Shape.Faces[1].Edges.append(mock_box.Shape.Faces[0].Edges[0])
        mock_cyl.Shape.Faces[1].Edges.append(mock_box.Shape.Faces[0].Edges[1])

        self._myNamer.addShape(mock_box)
        self._myNamer.modifyShape(newFaces, modifiedFaces)

        self.assertEqual(len(self._myNamer._tracker._realEdges), 14)

    def tearDown(self):
        pass

if __name__=='__main__':
    unittest.main()
