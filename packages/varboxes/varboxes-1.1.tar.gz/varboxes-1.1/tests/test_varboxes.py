#!/usr/bin/env python


"""
test varboxes modules
"""

import unittest
import time
import os


from varboxes import VarBox


class TestVarBox(unittest.TestCase):

    """all test concerning VarBox. """

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_set(self):
        varbox1 = VarBox(app_name='test_varbox')
        timestamp = time.time()
        varbox1.test_variable = timestamp

        self.assertEqual(timestamp, varbox1.test_variable)

        varbox2 = VarBox(app_name='test_varbox')

        self.assertTrue(hasattr(varbox2, 'test_variable'))

        self.assertEqual(timestamp, varbox2.test_variable)

    def test_save(self):
        """test save method

        """
        varbox1 = VarBox(app_name='test_varbox')
        timestamp = time.time()
        varbox1.test_list = list()
        varbox1.test_list.append(timestamp)

        varbox1.save()

        varbox2 = VarBox(app_name='test_varbox')

        self.assertEqual(len(varbox1.test_list), len(varbox2.test_list))
        self.assertEqual(timestamp, varbox2.test_list[0])

    def test_path(self):
        """test get_path method

        """
        vb1 = VarBox(app_name='test_varbox')
        vb1.a = 0
        vb2 = VarBox(app_name='test_varbox2')
        vb2.b = 1
        path1 = vb1.get_path()
        path2 = vb2.get_path()

        self.assertTrue(os.path.exists(path1))
        self.assertTrue(os.path.exists(path2))
        self.assertNotEqual(path1, path2)


if __name__ == '__main__':
    pass
