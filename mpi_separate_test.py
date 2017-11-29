import mpi_prep
import unittest
import doctest
import shutil
import StringIO
import os
from os.path import join

#a bunch of utilities that we're going to use across the testing suite.
class TestMPISeparateMethods(unittest.TestCase):

    def prep_dir(self, dir):
        if os.path.exists(dir):
            if os.path.isdir(dir):
                shutil.rmtree(dir)
            else:
                os.remove(dir)
        os.makedirs(dir)

    def setUp(self):
        self.prep_dir("test")
        self.prep_dir("test-stage")

    def tearDown(self):
        shutil.rmtree("test")
        shutil.rmtree("test-stage")

    def create_testfile(self, filename, content):
        with open(join("test", filename), "w") as file:
            file.write(content)

    def test_fileclasses_singleton(self):
        from mpi_prep import fileclasses
        singleton_file = ["test.jpg"]
        self.assertEquals(["test"], fileclasses(singleton_file, ".jpg"))

    def test_fileclasses_singleclass(self):
        from mpi_prep import fileclasses
        singleclass_files = ["test-1.jpg", "test-2.jpg"]
        self.assertEquals(["test"], fileclasses(singleclass_files, "-1.jpg"))

    def test_fileclasses_singletonmulticlass(self):
        from mpi_prep import fileclasses
        singletonmulticlass_files = ["test-1.jpg", "test-2.jpg"]
        self.assertEquals(["test-1", "test-2"], fileclasses(singletonmulticlass_files, ".jpg"))

    def test_fileclasses_multiclass(self):
        from mpi_prep import fileclasses
        multiclass_files = ["test-1-1.jpg", "test-1-2.jpg", "test-2-1.jpg", "test-2-2.jpg"]
        self.assertEquals(["test-1", "test-2"], fileclasses(multiclass_files, "-1.jpg"))

    def test_assemble_class(self):
        from mpi_prep import assembleclass
        self.create_testfile("test-1.jpg", "")
        self.create_testfile("test-2.jpg", "")
        assembleclass("test", "test-stage", "test-1")
        self.assertTrue(os.path.exists(join("test-stage","test-1")))
        self.assertTrue(os.path.exists(join("test-stage","test-1","test-1.jpg")))

doctest.testmod(mpi_prep, verbose=True)
unittest.main()
