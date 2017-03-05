import unittest
from unittest import mock
from TopoNamer import TopoNamer, TopoEdgeAndFaceTracker
from TestingHelpers import MockObjectMaker


class TestTracker(unittest.TestCase):
    '''Tests the Edges class found in TopoNamer'''
    def setUp(self):
        self.maker = MockObjectMaker()
        self.tracker = TopoEdgeAndFaceTracker()

    def test_makeName(self):
        self.tracker._faces = [None]
        self.tracker._edges = [None, None, None]
        name0 = self.tracker._makeName('Face')
        name1 = self.tracker._makeName('Edge')

        self.assertEqual(name0, 'Face0')
        self.assertEqual(name1, 'Edge2')

    def test_makeSubName(self):
        name0 = self.tracker._makeName('Face1', sub=True)
        name1 = self.tracker._makeName('Edge2bb', sub=True)
        name2 = self.tracker._makeName('Face1az', sub=True)
        name3 = self.tracker._makeName('Edge2z', sub=True)

        self.assertEqual(name0, 'Face1a')
        self.assertEqual(name1, 'Edge2bc')
        self.assertEqual(name2, 'Face1aaa')
        self.assertEqual(name3, 'Edge2aa')

    # def test_addEdge(self):
        # self.tracker._addEdge('Face0', 'Face1')

    def test_addFace(self):
        mock_face = self.maker.OCCFace()
        check_name = 'Face0'
        check_dict = {check_name:{'faceShape':mock_face,
                                  'openEdges':4}}

        facename = self.tracker.addFace(mock_face)

        self.assertEqual(facename, check_name)
        self.assertEqual(self.tracker._openFaceNames, check_dict)

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
                                'edgeNames':['Edge{}'.format(i) for i in range(4)]},
                       'Face1':{'faceIndex':1,
                                'edgeNames':['Edge{}'.format(i) for i in [4,0,5,6]]}}

        mock_face2.Edges[1].value = mock_face1.Edges[0].value

        name1 = self.tracker.addFace(mock_face1)
        name2 = self.tracker.addFace(mock_face2)

        self.assertEqual(self.tracker._faceNames, check_dict)

    def test_addThreeFacesWithSeparateSharedEdges(self):
        mock_face1 = self.maker.OCCFace()
        mock_face2 = self.maker.OCCFace()
        mock_face3 = self.maker.OCCFace()

        check_dict  = {'Face0':{'faceIndex':0,
                                'edgeNames':['Edge{}'.format(i) for i in range(4)]},
                       'Face1':{'faceIndex':1,
                                'edgeNames':['Edge{}'.format(i) for i in [4,0,5,6]]},
                       'Face2':{'faceIndex':2,
                                'edgeNames':['Edge{}'.format(i) for i in [7,8,1,9]]}}

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
                                'edgeNames':['Edge{}'.format(i) for i in range(4)]},
                       'Face1':{'faceIndex':1,
                                'edgeNames':['Edge{}'.format(i) for i in [0,4,5,6]]},
                       'Face2':{'faceIndex':2,
                                'edgeNames':['Edge{}'.format(i) for i in [4,7,8,9]]}}

        mock_face1.Edges[0].value = mock_face0.Edges[0].value
        mock_face2a.Edges[0].value = mock_face0.Edges[1].value
        mock_face2b.Edges[0].value = mock_face1.Edges[1].value

        self.tracker.addFace(mock_face0) # Edges 0 - 3
        self.tracker.addFace(mock_face1) # Edges 0 and 4 - 6
        facename = self.tracker.addFace(mock_face2a) # Edges 1 and 7 - 9

        self.tracker.modifyFace(facename, mock_face2b) # Edges 4 and 7-9

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
