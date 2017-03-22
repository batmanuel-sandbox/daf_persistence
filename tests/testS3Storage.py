#!/usr/bin/env python

#
# LSST Data Management System
# Copyright 2017 LSST Corporation.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#

import getpass
import lsst.daf.persistence as dp
import lsst.daf.persistence.test as dpTest
from lsst.utils import getPackageDir
import lsst.utils.tests
import os
import pickle
import shutil
import sys
import time
import unittest
import uuid

packageDir = os.path.join(getPackageDir('daf_persistence'))


class TestMapper:
    pass


def setup_module(module):
    lsst.utils.tests.init()


class TestS3Storage(unittest.TestCase):
    """A test case for getting the relative path to parent from a symlink in PosixStorage."""

    testDir = os.path.join(packageDir, 'tests', 'TestS3Storage')

    def setUp(self):
        # TODO need some way choosing to run only if the credentials are set up

        authServer = "s3://lsst.signin.aws.amazon.com/console"
        self.container1Name = "{}.testContainer.{}".format(
            getpass.getuser(), int(time.time()))
        self.container2Name = "{}.testContainer.{}".format(
            getpass.getuser(), int(time.time()))
        self.uri = \
            "{}/{}".format(authServer, self.container1Name)
        self.uri2 = \
            "{}/{}".format(authServer, self.container2Name)
        self.tearDown()

    # def tearDown(self):
        # for uri in (self.uri, self.uri2):
        #     storage = dp.S3Storage(uri=uri)
        #     if storage and storage.containerExists():
        #         storage.deleteContainer()
        #     if os.path.exists(TestS3Storage.testDir):
        #         shutil.rmtree(TestS3Storage.testDir)

    # def testParseURI(self):
    #     """Test that S3Storage._parseURI returns the proper values and
    #     raises the proper exceptions."""
    #     uri = "s3://lsst.signin.aws.amazon.com/console/testContainer"
    #     res = dp.S3Storage._parseURI(uri)
    #     self.assertEqual(res, ('s3', 'lsst.signin.aws.amazon.com',
    #                            'testContainer'))
    #     with self.assertRaises(RuntimeError):
    #         dp.S3Storage._parseURI("file://foo/bar")
    #     with self.assertRaises(RuntimeError):
    #         dp.S3Storage._parseURI("foo/bar")
    #     with self.assertRaises(RuntimeError):
    #         dp.S3Storage._parseURI(
    #             "s3://nebula.ncsa.illinois.edu:5000/v2.0/LSST/testContainer")

    def testS3Storage(self):
        """Verify that S3Storage implements all the StorageInterface
        functions."""
        import pdb; pdb.set_trace()
        storage = dp.S3Storage(uri=self.uri)
        self.assertEqual(storage._containerName, self.container1Name)
        self.assertTrue(storage.containerExists())
        # # Test containerExists by changing the container name so that it will
        # # return false, and then put the name back.
        # containerName = storage._containerName
        # storage._containerName = "foo"
        # self.assertFalse(storage.containerExists())
        # storage._containerName = containerName

        # testObject = dpTest.TestObject("abc")
        # butlerLocation = dp.ButlerLocation(
        #     pythonType='lsst.daf.persistence.test.TestObject', cppType=None,
        #     storageName='PickleStorage', locationList='firstTestObject',
        #     dataId={}, mapper=None, storage=storage)

        # # Test writing an object to storage
        # storage.write(butlerLocation, testObject)
        # # Test getting a local copy of the file in storage.
        # localFile = storage.getLocalFile('firstTestObject')
        # # Test reading the file in a new object using the localFile's name, as
        # # well as using the localFile handle directly.
        # for f in (open(localFile.name, 'r'), localFile):
        #     if sys.version_info.major >= 3:
        #         obj = pickle.load(f, encoding="latin1")
        #     else:
        #         obj = pickle.load(f)
        #     self.assertEqual(testObject, obj)
        # # Test reading the butlerLocation, should return the object instance.
        # reloadedObject = storage.read(butlerLocation)
        # self.assertEqual(testObject, reloadedObject[0])
        # # Test the 'exists' function with a string
        # self.assertTrue(storage.exists('firstTestObject'))
        # self.assertFalse(storage.exists('secondTestObject'))
        # # Test the 'exists' function with a ButlerLocation. (note that most of
        # # the butler location fields are unused in exists and so are set to
        # # None here.)
        # location = dp.ButlerLocation(
        #     pythonType=None, cppType=None, storageName=None,
        #     locationList=['firstTestObject'], dataId={}, mapper=None,
        #     storage=None)
        # self.assertTrue(storage.exists(location))
        # location = dp.ButlerLocation(
        #     pythonType=None, cppType=None, storageName=None,
        #     locationList=['secondTestObject'], dataId={}, mapper=None,
        #     storage=None)
        # self.assertFalse(storage.exists(location))
        # # Test the 'instanceSearch' function, with and without the fits header
        # # extension
        # self.assertEqual(storage.instanceSearch('firstTestObject'),
        #                  ['firstTestObject'])
        # self.assertEqual(storage.instanceSearch('firstTestObject[1]'),
        #                  ['firstTestObject[1]'])
        # self.assertEqual(storage.instanceSearch('first*Object'),
        #                  ['firstTestObject'])
        # self.assertEqual(storage.instanceSearch('*TestObject[1]'),
        #                  ['firstTestObject[1]'])
        # self.assertIsNone(storage.instanceSearch('secondTestObject'))
        # self.assertIsNone(storage.instanceSearch('secondTestObject[1]'))
        # # Test the 'search' function
        # self.assertEqual(storage.search(self.uri, 'firstTestObject'),
        #                  ['firstTestObject'])
        # # Test the copy function
        # storage.copyFile('firstTestObject', 'secondTestObject')
        # with self.assertRaises(RuntimeError):
        #     storage.copyFile('thirdTestObject', 'fourthTestObject')
        # # Test locationWithRoot
        # self.assertEqual(storage.locationWithRoot('firstTestObject'),
        #                  self.uri + '/' + 'firstTestObject')
        # # Test getRepositoryCfg and putRepositoryCfg
        # repositoryCfg = dp.RepositoryCfg.makeFromArgs(dp.RepositoryArgs(
        #     root=self.uri, mapper=TestMapper),
        #     parents=None)
        # storage.putRepositoryCfg(repositoryCfg)
        # reloadedRepoCfg = storage.getRepositoryCfg(self.uri)
        # self.assertEqual(repositoryCfg, reloadedRepoCfg)
        # # Test getting a non-existant RepositoryCfg
        # self.assertIsNone(storage.getRepositoryCfg(self.uri2))
        # # Test getting the mapper class from the repoCfg in the repo.
        # mapper = dp.S3Storage.getMapperClass(self.uri)
        # self.assertEqual(mapper, TestMapper)
        # # Test for a repoCfg that resides outside its repository; it has a
        # # root that is not the same as its location.
        # repositoryCfg = dp.RepositoryCfg.makeFromArgs(dp.RepositoryArgs(
        #     root='foo/bar/baz', mapper='lsst.obs.base.CameraMapper'),
        #     parents=None)
        # storage.putRepositoryCfg(repositoryCfg, loc=self.uri)
        # reloadedRepoCfg = storage.getRepositoryCfg(self.uri)
        # self.assertEqual(repositoryCfg, reloadedRepoCfg)

        # storage.deleteContainer()
        # self.assertFalse(storage.containerExists())


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


if __name__ == '__main__':
    lsst.utils.tests.init()
    unittest.main()
