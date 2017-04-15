import unittest
from TopoNamer.TopoTracker import TopoTracker
from test.TestingHelpers import MockObjectMaker

class TestTracker(unittest.TestCase):
    def setUp(self):
        self.maker = MockObjectMaker()
        self.tracker = TopoTracker()

    def test_makeName(self):
        self.tracker._numbFaces = 0
        self.tracker._numbEdges = 2
        name0 = self.tracker._makeName('Face')
        name1 = self.tracker._makeName('Edge')

        self.assertEqual(name0, 'Face000')
        self.assertEqual(name1, 'Edge002')
        name1 = self.tracker._makeName('Edge')
        self.assertEqual(name1, 'Edge003')

    def test_makeSubName(self):
        name0 = self.tracker._makeName('Face001', sub=True)
        name1 = self.tracker._makeName('Edge002bb', sub=True)
        name2 = self.tracker._makeName('Face001az', sub=True)
        name3 = self.tracker._makeName('Edge002z', sub=True)

        self.assertEqual(name0, 'Face001a')
        self.assertEqual(name1, 'Edge002bc')
        self.assertEqual(name2, 'Face001aaa')
        self.assertEqual(name3, 'Edge002aa')


class TestTracker_legacy(object):
    '''This tester is no longer valid. We\'ll just use it as a basis  for the real tracker
    above'''

    def test_addEdge(self):
        self.tracker._addEdge('Face000', 'Face001')
        edges = {'Edge000':{'faceNames':['Face000', 'Face001'],
                            'valid':True}}

        self.assertEqual(self.tracker._edgeNames, edges)

    def test_getEdge(self):
        face0 = self.maker.OCCFace()
        face1 = self.maker.OCCFace()
        face1.Edges[0] = face0.Edges[0]
        self.tracker._edgeNames = {'Edge000':{'faceNames':['Face000', 'Face001'],
                                              'valid':True}}
        self.tracker._faceNames = {'Face000':{'faceShape':face0},
                                   'Face001':{'faceShape':face1}}

        edge = self.tracker.getEdge('Edge000')
        self.assertEqual(edge, face0.Edges[0])

    def test_getEdgeInvalidNameError(self):
        self.assertRaises(KeyError, self.tracker.getEdge, 'Edge000')

    def test_getEdgeNoTwoFacesError(self):
        face0 = self.maker.OCCFace()
        face1 = self.maker.OCCFace()
        self.tracker._edgeNames = {'Edge000':{'faceNames':['Face000', 'Face001'],
                                              'valid':True}}
        self.tracker._faceNames = {'Face000':{'faceShape':face0},
                                   'Face001':{'faceShape':face1}}

        self.assertRaises(ValueError, self.tracker.getEdge, 'Edge000')

    def test_checkForNewEdgesWithNoSharedEdge(self):
        face0 = self.maker.OCCFace()
        face1 = self.maker.OCCFace()
        edge = self.maker.OCCEdge()
        open_faces = {'Face000':{'faceShape':face0,
                                 'openEdgeIndices':list(range(4))}}
        self.tracker._faceNames = open_faces.copy()

        indices = self.tracker._checkForNewEdges(face1, 'Face001')
        self.assertEqual(self.tracker._faceNames, open_faces)
        self.assertEqual(self.tracker._edgeNames, {})
        self.assertEqual(indices, [0,1,2,3])

    def test_checkForNewEdgesWithOneSharedEdge(self):
        face0 = self.maker.OCCFace()
        face1 = self.maker.OCCFace()
        face1.Edges[0] = face0.Edges[0]
        open_faces = {'Face000':{'faceShape':face0,
                                'openEdgeIndices':list(range(4))}}
        edges = {'Edge000':{'faceNames':['Face000', 'Face001'],
                            'valid':True}}

        self.tracker._faceNames = open_faces.copy()
        indices = self.tracker._checkForNewEdges(face1, 'Face001')

        open_faces['Face000']['openEdgeIndices'] = [1,2,3]
        self.assertEqual(self.tracker._faceNames, open_faces)
        self.assertEqual(self.tracker._edgeNames, edges)
        self.assertEqual(indices, [1,2,3])

    # def test_checkEdges(self):
        # edgeNames = {'Edge000':['Face000', 'Face001']}
        # self.tracker._edgeNames = edgeNames.copy()
        # self.tracker._faceNames = {'Face000':{'openEdges':0},
                                   # 'Face001':{'openEdges':0}}
        # self.tracker._checkEdges()
        # self.assertEqual(self.tracker._edgeNames, edgeNames)

    # def test_checkEdgesSomeRemoved(self):
        # self.tracker._edgeNames = {'Edge000':['Face000', 'Face001'],
                                   # 'Edge001':['Face002', 'Face003'],
                                   # 'Edge002':['Face002', 'Face004'],
                                   # 'Edge003':['Face001', 'Face003']}
        # self.tracker._faceNames = {'Face000':{'openEdges':1},
                                   # 'Face001':{'openEdges':0},
                                   # 'Face002':{'openEdges':0},
                                   # 'Face003':{'openEdges':0},
                                   # 'Face004':{'openEdges':1}}
        # self.tracker._checkEdges()
        # self.assertEqual(self.tracker._edgeNames,
                # {'Edge000':None,
                 # 'Edge001':['Face002', 'Face003'],
                 # 'Edge002':None,
                 # 'Edge003':['Face001', 'Face003']})

    def test_addFace(self):
        mock_face = self.maker.OCCFace()
        check_name = 'Face000'
        check_dict = {check_name:{'faceShape':mock_face,
                                  'openEdgeIndices':list(range(4))}}

        facename = self.tracker.addFace(mock_face)

        self.assertEqual(facename, check_name)
        self.assertEqual(self.tracker._faceNames, check_dict)

    def test_addSameFaceError(self):
        mock_faces = [self.maker.OCCFace() for i in list(range(6))]
        mock_faces[5].value = mock_faces[0].value
        for mock_face in mock_faces[:5]:
            self.tracker.addFace(mock_face)
        self.assertRaises(ValueError, self.tracker.addFace, mock_faces[5])

    def test_addTwoFacesWithZeroSharedEdges(self):
        mock_face1  = self.maker.OCCFace()
        mock_face2  = self.maker.OCCFace()
        check_name0 = 'Face000'
        check_name1 = 'Face001'
        open_faces  = {check_name0:{'faceShape':mock_face1,
                                    'openEdgeIndices':list(range(4))},
                       check_name1:{'faceShape':mock_face2,
                                    'openEdgeIndices':list(range(4))}}

        name0 = self.tracker.addFace(mock_face1)
        name1 = self.tracker.addFace(mock_face2)

        self.assertEqual(self.tracker._faceNames, open_faces)
        self.assertEqual(name0, check_name0)
        self.assertEqual(name1, check_name1)

    def test_addTwoFacesWithSharedEdge(self):
        mock_face0 = self.maker.OCCFace()
        mock_face1 = self.maker.OCCFace()
        open_faces  = {'Face000':{'faceShape':mock_face0,
                                  'openEdgeIndices':[1,2,3]},
                       'Face001':{'faceShape':mock_face1,
                                  'openEdgeIndices':[1,2,3]}}
        edges = {'Edge000': {'faceNames':['Face000', 'Face001'],
                            'valid':True}}

        mock_face1.Edges[0] = mock_face0.Edges[0]

        name1 = self.tracker.addFace(mock_face0)
        name2 = self.tracker.addFace(mock_face1)

        self.assertEqual(self.tracker._faceNames, open_faces)
        self.assertEqual(self.tracker._edgeNames, edges)

    def test_addThreeFacesWithSeparateSharedEdges(self):
        mock_face0 = self.maker.OCCFace()
        mock_face1 = self.maker.OCCFace()
        mock_face2 = self.maker.OCCFace()

        mock_face1.Edges[1].value = mock_face0.Edges[0].value
        mock_face2.Edges[2].value = mock_face0.Edges[1].value

        face_names  = {'Face000':{'faceShape':mock_face0,
                                'openEdgeIndices':range(2,2)},
                       'Face001':{'faceShape':mock_face1,
                                'openEdgeIndices':range(1,3)},
                       'Face002':{'faceShape':mock_face2,
                                'openEdgeIndices':range(1,3)}}
        edges = {'Edge000':{'faceNames':['Face000', 'Face001'],
                           'valid':True},
                'Edge001':{'faceNames':['Face000', 'Face002'],
                           'valid':True}}

        name1 = self.tracker.addFace(mock_face0)
        name2 = self.tracker.addFace(mock_face1)
        name3 = self.tracker.addFace(mock_face2)

        self.assertEqual(self.tracker._faceNames, face_names)
        self.assertEqual(self.tracker._edgeNames, edges)

    def test_addThreeFacesWithSharedEdgeError(self):
        mock_face0 = self.maker.OCCFace()
        mock_face1 = self.maker.OCCFace()
        mock_face2 = self.maker.OCCFace()

        mock_face1.Edges[2] = mock_face0.Edges[0]
        mock_face2.Edges[3] = mock_face0.Edges[0]

        index1 = self.tracker.addFace(mock_face0)
        index2 = self.tracker.addFace(mock_face1)
        import pprint
        pprint.pprint(self.tracker._faceNames)
        pprint.pprint(self.tracker._edgeNames)
        import pdb; pdb.set_trace()

        self.assertRaises(ValueError, self.tracker.addFace, mock_face2)

    def test_modifyFaceWithMovedFace(self):
        mock_face0 = self.maker.OCCFace()
        mock_face1 = self.maker.OCCFace()
        mock_face2a = self.maker.OCCFace()
        mock_face2b = self.maker.OCCFace()
        check_dict  = {'Face000':{'faceShape':mock_face0,
                                'openEdgeIndices':range(1,3)},
                       'Face001':{'faceShape':mock_face1,
                                'openEdgeIndices':range(2,2)},
                       'Face002':{'faceShape':mock_face2b,
                                'openEdgeIndices':range(1,3)}}

        mock_face1.Edges[0].value = mock_face0.Edges[0].value
        mock_face2a.Edges[0].value = mock_face0.Edges[1].value
        mock_face2b.Edges[0].value = mock_face1.Edges[1].value

        self.tracker.addFace(mock_face0) # Edges 0 - 3
        self.tracker.addFace(mock_face1) # Edges 0 and 4 - 6
        facename = self.tracker.addFace(mock_face2a) # Edges 1 and 7 - 9

        self.tracker.modifyFace(facename, mock_face2b) # Edges 4 and 7-9

        self.assertEqual(self.tracker._faceNames, check_dict)

    def test_modifyFaceWithNewEdge(self):
        # Face 2b will cut across Face0 such that face0 now has 5 edges instead of just 4.
        # The new edge on Face0 will be an entire edge from face 1b. In other words,
        # imagine two perpendicular faces. Now, take the top edge of the vertical face and
        # place it across the mid-point of two edges on the horizontal face. Now truncate
        # the horizontal face such that it is no longer a square. The vertical face
        # remains a square.
        mock_face0a = self.maker.OCCFace()
        mock_face0b = self.maker.OCCFace()
        mock_face1 = self.maker.OCCFace()
        check_dict  = {'Face000':{'faceShape':mock_face0b,
                                'openEdgeIndices':list(range(4))},
                       'Face001':{'faceShape':mock_face1,
                                'openEdgeIndices':range(1,3)}}

        # really most of these Edges will change, but for this test that is not relevant.
        mock_face0b.Edges = mock_face0a.Edges
        mock_face0b.Edges.append(mock_face1.Edges[0])

        faceName = self.tracker.addFace(mock_face0a) # horizontal face

        self.tracker.addFace(mock_face1) # vertical face
        self.tracker.modifyFace(faceName, mock_face0b)

        self.assertEqual(self.tracker._faceNames, check_dict)

