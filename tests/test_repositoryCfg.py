#
# LSST Data Management System
# Copyright 2016 LSST Corporation.
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
from builtins import object

import copy
import os
import shutil
import tempfile
import unittest
import yaml

import lsst.daf.persistence as dp
from lsst.daf.persistence.test.utils import makeOldButlerRepo
import lsst.daf.persistence.test as dpTest
import lsst.utils.tests

# Define the root of the tests relative to this file
ROOT = os.path.abspath(os.path.dirname(__file__))


class TestCfgRelationship(unittest.TestCase):

    testDir = os.path.join(ROOT, 'TestCfgRelationship')

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        if os.path.exists(self.testDir):
            shutil.rmtree(self.testDir)

    def testRWModes(self):
        args = dp.RepositoryArgs(mode='w', mapper=dpTest.EmptyTestMapper,
                                 root=os.path.join(self.testDir, 'repositoryCfg'))
        butler = dp.Butler(outputs=args)
        # inputs must be read-only or read-write and not write-only
        args = dp.RepositoryArgs(mode='r', mapper=dpTest.EmptyTestMapper,
                                 root=os.path.join(self.testDir, 'repositoryCfg'))
        butler = dp.Butler(inputs=args)
        args = dp.RepositoryArgs(mode='rw', mapper=dpTest.EmptyTestMapper,
                                 root=os.path.join(self.testDir, 'repositoryCfg'))
        butler = dp.Butler(inputs=args)
        args = dp.RepositoryArgs(mode='w', mapper=dpTest.EmptyTestMapper,
                                 root=os.path.join(self.testDir, 'repositoryCfg'))
        self.assertRaises(RuntimeError, dp.Butler, inputs=args)

        # outputs must be write-only or read-write and not read-only
        args = dp.RepositoryArgs(mode='w', mapper=dpTest.EmptyTestMapper,
                                 root=os.path.join(self.testDir, 'repositoryCfg'))
        butler = dp.Butler(outputs=args)
        args = dp.RepositoryArgs(mode='rw', mapper=dpTest.EmptyTestMapper,
                                 root=os.path.join(self.testDir, 'repositoryCfg'))
        butler = dp.Butler(outputs=args)
        args = dp.RepositoryArgs(mode='r', mapper=dpTest.EmptyTestMapper,
                                 root=os.path.join(self.testDir, 'repositoryCfg'))
        self.assertRaises(RuntimeError, dp.Butler, outputs=args)

    def testExistingParents(self):
        # parents of inputs should be added to the inputs list
        butler = dp.Butler(outputs=dp.RepositoryArgs(mode='w',
                                                     mapper=dpTest.EmptyTestMapper,
                                                     root=os.path.join(self.testDir, 'repositoryCfg/a')))
        del butler
        butler = dp.Butler(inputs=os.path.join(self.testDir, 'repositoryCfg/a'),
                           outputs=os.path.join(self.testDir, 'repositoryCfg/b'))
        del butler
        butler = dp.Butler(inputs=os.path.join(self.testDir, 'repositoryCfg/b'))
        self.assertEqual(len(butler._repos.inputs()), 2)
        # verify serach order:
        self.assertEqual(butler._repos.inputs()[0].cfg.root, os.path.join(self.testDir, 'repositoryCfg/b'))
        self.assertEqual(butler._repos.inputs()[1].cfg.root, os.path.join(self.testDir, 'repositoryCfg/a'))
        self.assertEqual(len(butler._repos.outputs()), 0)

        butler = dp.Butler(outputs=dp.RepositoryArgs(cfgRoot=os.path.join(self.testDir, 'repositoryCfg/b'),
                                                     mode='rw'))
        # verify serach order:
        self.assertEqual(butler._repos.inputs()[0].cfg.root, os.path.join(self.testDir, 'repositoryCfg/b'))
        self.assertEqual(butler._repos.inputs()[1].cfg.root, os.path.join(self.testDir, 'repositoryCfg/a'))
        self.assertEqual(len(butler._repos.outputs()), 1)
        self.assertEqual(butler._repos.outputs()[0].cfg.root, os.path.join(self.testDir, 'repositoryCfg/b'))

        butler = dp.Butler(inputs=os.path.join(self.testDir, 'repositoryCfg/a'),
                           outputs=dp.RepositoryArgs(cfgRoot=os.path.join(self.testDir, 'repositoryCfg/b'),
                                                     mode='rw'))
        self.assertEqual(len(butler._repos.inputs()), 2)
        # verify serach order:
        self.assertEqual(butler._repos.inputs()[0].cfg.root, os.path.join(self.testDir, 'repositoryCfg/b'))
        self.assertEqual(butler._repos.inputs()[1].cfg.root, os.path.join(self.testDir, 'repositoryCfg/a'))
        self.assertEqual(len(butler._repos.outputs()), 1)
        self.assertEqual(butler._repos.outputs()[0].cfg.root, os.path.join(self.testDir, 'repositoryCfg/b'))

        # parents of write-only outputs must be be listed with the inputs
        with self.assertRaises(RuntimeError):
            butler = dp.Butler(outputs=os.path.join(self.testDir, 'repositoryCfg/b'))
        butler = dp.Butler(inputs=os.path.join(self.testDir, 'repositoryCfg/a'),
                           outputs=os.path.join(self.testDir, 'repositoryCfg/b'))
        self.assertEqual(len(butler._repos.inputs()), 1)
        self.assertEqual(len(butler._repos.outputs()), 1)
        self.assertEqual(butler._repos.outputs()[0].cfg.root, os.path.join(self.testDir, 'repositoryCfg/b'))

        # add a new parent to an existing output
        butler = dp.Butler(outputs=dp.RepositoryArgs(mode='w',
                                                     mapper=dpTest.EmptyTestMapper,
                                                     root=os.path.join(self.testDir, 'repositoryCfg/c')))
        butler = dp.Butler(inputs=(os.path.join(self.testDir, 'repositoryCfg/a'),
                                   os.path.join(self.testDir, 'repositoryCfg/c')),
                           outputs=os.path.join(self.testDir, 'repositoryCfg/b'))

        # should raise if the input order gets reversed:
        with self.assertRaises(RuntimeError):
            butler = dp.Butler(inputs=(os.path.join(self.testDir, 'repositoryCfg/c'),
                                       os.path.join(self.testDir, 'repositoryCfg/a')),
                               outputs=os.path.join(self.testDir, 'repositoryCfg/b'))


    def testSymLinkInPath(self):
        """Test that when a symlink is in an output repo path that the repoCfg
        stored in the output repo has a parent path from the actual output
        lcoation to the input repo."""
        # create a repository at 'a'
        repoADir = os.path.join(self.testDir, 'repositoryCfg/a')
        repoBDir = os.path.join(self.testDir, 'repositoryCfg/b')
        butler = dp.Butler(outputs=dp.RepositoryArgs(
            mode='w', mapper=dpTest.EmptyTestMapper,
            root=repoADir))
        # create a symlink from 'b' to a temporary directory
        tmpDir = tempfile.mkdtemp()
        os.symlink(tmpDir, repoBDir)
        # create an output repo at 'b' with the input repo 'a'
        butler = dp.Butler(inputs=repoADir, outputs=repoBDir)
        # verify a repoCfg in the tmp dir with a proper parent path from tmp
        # to 'a' (not from 'b' to 'a')
        cfg = dp.PosixStorage.getRepositoryCfg(tmpDir)
        # verify that the parent link gotten via the symlink target is a path
        # to A
        self.assertEqual(repoADir, cfg.parents[0])
        cfg = dp.PosixStorage.getRepositoryCfg(repoBDir)
        # also verify that the parent gotten via the symlink is a path to A
        self.assertEqual(repoADir, cfg.parents[0])

    def testStorageRepoCfgCache(self):
        """Tests that when a cfg is gotten from storage it is cached."""
        butler = dp.Butler(outputs=dp.RepositoryArgs(mode='w',
                                                     mapper=dpTest.EmptyTestMapper,
                                                     root=os.path.join(self.testDir, 'repositoryCfg/a')))
        del butler
        storage = dp.Storage()
        self.assertEqual(0, len(storage.repositoryCfgs))
        cfg = storage.getRepositoryCfg(os.path.join(self.testDir, 'repositoryCfg/a'))
        self.assertEqual(cfg, storage.repositoryCfgs[os.path.join(self.testDir, 'repositoryCfg/a')])


class TestNestedCfg(unittest.TestCase):

    rootDir = os.path.join(ROOT, 'repositoryCfg_TestNestedCfg')

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        if os.path.exists(self.rootDir):
            shutil.rmtree(self.rootDir)

    def test(self):
        parentCfg = dp.RepositoryCfg(root=os.path.join(self.rootDir, 'parent'),
                                     mapper='lsst.daf.persistence.SomeMapper',
                                     mapperArgs = {},
                                     parents=None,
                                     policy=None)
        cfg = dp.RepositoryCfg(root=self.rootDir,
                               mapper='lsst.daf.persistence.SomeMapper',
                               mapperArgs = {},
                               parents=[parentCfg],
                               policy=None)
        dp.PosixStorage.putRepositoryCfg(cfg)
        reloadedCfg = dp.PosixStorage.getRepositoryCfg(self.rootDir)
        self.assertEqual(cfg, reloadedCfg)
        self.assertEqual(cfg.parents[0], parentCfg)


class TestExtendParentsWithOldButlerParent(unittest.TestCase):

    testDir = os.path.join(ROOT, 'TestExtendParentsWithOldButlerParent')

    def setUp(self):
        if os.path.exists(self.testDir):
            shutil.rmtree(self.testDir)
        self.repoADir = os.path.join(self.testDir, 'a')
        makeOldButlerRepo(self.repoADir, 'lsst.daf.persistence.test.EmptyTestMapper')

    def tearDown(self):
        if os.path.exists(self.testDir):
            shutil.rmtree(self.testDir)

    def test(self):
        repoBDir = os.path.join(self.testDir, 'b')
        butler = dp.Butler(inputs={'root': self.repoADir, 'mapperArgs': {'calibRoot': '/CALIB'}},
                           outputs=repoBDir)
        del butler
        butler = dp.Butler(inputs={'root': self.repoADir},
                           outputs=repoBDir)
        del butler


# "fake" repository version 0
class RepositoryCfg(yaml.YAMLObject):
    yaml_tag = u"!RepositoryCfg_v0"

    def __init__(self, mapper, mapperArgs):
        self._mapper = mapper
        self._mapperArgs = mapperArgs

    @staticmethod
    def v0Constructor(loader, node):
        d = loader.construct_mapping(node)
        return dp.RepositoryCfg(root=d['_root'], mapper=None, mapperArgs=None, parents=None, policy=None)


yaml.add_constructor(u"!RepositoryCfg_v0", RepositoryCfg.v0Constructor)


class TestCfgFileVersion(unittest.TestCase):
    """Proof-of-concept test case for a fictitious version 0 of a persisted repository cfg.
    """

    testDir = os.path.join(ROOT, 'TestCfgFileVersion')

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        if os.path.exists(self.testDir):
            shutil.rmtree(self.testDir)

    def test(self):
        os.makedirs(os.path.join(self.testDir, 'repositoryCfg'))
        f = open(os.path.join(self.testDir, 'repositoryCfg/repositoryCfg.yaml'), 'w')
        f.write("""!RepositoryCfg_v0
                   _root: 'foo/bar'""")
        f.close()
        cfg = dp.PosixStorage.getRepositoryCfg(os.path.join(self.testDir, 'repositoryCfg'))


class TestExtendParents(unittest.TestCase):
    """Test for the RepositoryCfg.extendParents function.
    """

    def test(self):
        cfg = dp.RepositoryCfg(root='.', mapper='my.mapper.class', mapperArgs=None,
                               parents=['bar', 'baz'], policy=None)
        cfg.extendParents(['bar', 'baz', 'qux'])
        with self.assertRaises(dp.ParentsMismatch):
            cfg.extendParents(['bar', 'baz', 'corge'])

    # todo include a repositoryCfg in parents lists in this test


class TestMapperArgsNone(unittest.TestCase):
    """Tests that the RepositoryCfg.mapperArgs is converted to a dict if None is passed in.
    """
    def test(self):
        cfg = dp.RepositoryCfg(root='foo', mapper='foo', mapperArgs=None, parents=None, policy=None)
        self.assertIsInstance(cfg.mapperArgs, dict)


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()

if __name__ == '__main__':
    lsst.utils.tests.init()
    unittest.main()
