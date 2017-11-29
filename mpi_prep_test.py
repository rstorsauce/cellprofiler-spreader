import mpi_prep
import unittest
import doctest
import shutil
import StringIO
import os
from os.path import join

#a bunch of utilities that we're going to use across the testing suite.
class TestMPIPrepMethods(unittest.TestCase):

    def setUp(self):
        if os.path.exists("test"):
            if os.path.isdir("test"):
                shutil.rmtree("test")
            else:
                os.remove("test")
        os.makedirs("test")

    def tearDown(self):
        shutil.rmtree("test")

    def create_testfile(self, filename, content):
        with open(join("test", filename), "w") as file:
            file.write(content)

    def create_collationfile(self, filename, content):
        if not os.path.exists(join("test","content")):
            os.makedirs(join("test","content"))
        with open(join("test","content", filename), "w") as file:
            file.write(content)

    def test_isimagefile(self):
        from mpi_prep import isimagefile

        self.assertTrue(isimagefile("test.jpg"))
        self.assertTrue(isimagefile("test.png"))
        self.assertTrue(isimagefile("test.tif"))
        self.assertTrue(isimagefile("test.tiff"))
        self.assertFalse(isimagefile("test.csv"))

    def test_firstline(self):
        from mpi_prep import first_line
        self.create_testfile("test", "this is the first line.\nthis is the last line.\n")
        with open(join("test", "test"), "r") as file:
            self.assertEquals(first_line(file), "this is the first line.")

    def test_lastline(self):
        from mpi_prep import last_line
        #first, build a "lastline" file.
        self.create_testfile("test", "this is the first line.\nthis is the last line.")
        with open(join("test", "test"), "r") as file:
            self.assertEquals(last_line(file), "this is the last line.")

        self.create_testfile("test", "this is the first line.\nthis is the last line.\n")
        with open(join("test", "test"), "r") as file:
            self.assertEquals(last_line(file), "this is the last line.")

    def test_get_column(self):
        from mpi_prep import get_column
        self.create_testfile("test", "A,B,C,ImageNumber,E,F\n1,2,3,1,4,5\n")
        with open(join("test", "test"), "r") as file:
            self.assertEquals(get_column(file, "A"), 0)
            self.assertEquals(get_column(file, "ImageNumber"), 3)

    def test_substitute_column(self):
        from mpi_prep import substitute_column
        self.assertEquals("1,2,3,2,4,5", substitute_column("1,2,3,1,4,5", 3, "2"))

    def test_collate_image_file(self):
        from mpi_prep import collate_image_file
        file = "test_img.jpg"
        self.create_collationfile(file, "")
        #next execute the collation process.
        collate_image_file("test", "content", file)
        #check that there no longer is a content directory.
        self.assertFalse(os.path.exists(join("test", "content", file)))
        #check that the test_img.jpg file exists.
        self.assertTrue(os.path.exists(join("test", file)))

    def test_collate_image_manifest_into_empty(self):
        from mpi_prep import collate_image_manifest
        file = "test_manifest.csv"
        manifest_content = "A,B,C,ImageNumber,E,F\n1,2,3,1,4,5\n"
        self.create_collationfile(file, manifest_content)
        collate_image_manifest("test", "content", file, "content")
        self.assertTrue(os.path.exists(join("test", file)))
        with open(join("test", file), 'r') as content_file:
            self.assertEquals(content_file.read(), manifest_content)

    def test_collate_image_manifest_into_existing(self):
        from mpi_prep import collate_image_manifest
        file = "test_manifest.csv"
        manifest_content = "A,B,C,ImageNumber,Group_Index,F\n1,2,3,1,1,5\n"
        combined_manifest = "A,B,C,ImageNumber,Group_Index,F\n1,2,3,1,1,5\n1,2,3,2,2,5\n"
        self.create_testfile(file, manifest_content)
        self.create_collationfile(file, manifest_content)
        collate_image_manifest("test","content", file, "content")
        self.assertTrue(os.path.exists(join("test", file)))
        with open(join("test", file), 'r') as content_file:
            self.assertEquals(content_file.read(), combined_manifest)

    def test_collate_multiple_image_manifest_into_existing(self):
        from mpi_prep import collate_image_manifest
        file = "test_manifest.csv"
        manifest_content = "A,B,C,ImageNumber,E,F\n1,2,3,1,4,5\n1,2,3,2,4,5\n"
        combined_manifest = "A,B,C,ImageNumber,E,F\n1,2,3,1,4,5\n1,2,3,2,4,5\n1,2,3,3,4,5\n1,2,3,4,4,5\n"
        self.create_testfile(file, manifest_content)
        self.create_collationfile(file, manifest_content)
        collate_image_manifest("test","content", file, "content")
        self.assertTrue(os.path.exists(join("test", file)))
        with open(join("test", file), 'r') as content_file:
            self.assertEquals(content_file.read(), combined_manifest)

    def test_isimagemanifest(self):
        from mpi_prep import isimagemanifest
        file = "test_manifest.csv"
        manifest_content = "A,B,C,ImageNumber,E,F\n1,2,3,1,4,5\n"
        self.create_collationfile(file, manifest_content)
        self.assertTrue(isimagemanifest(join("test", "content", file)))

    def test_collate_datafile_into_empty(self):
        from mpi_prep import collate_data_file
        file = "test_datafile.csv"
        datafile_content = "ImageNumber,A,B,C,D,E\n1,2,3,4,5,6\n"
        self.create_collationfile(file, datafile_content)
        collate_data_file("test","content",file)
        self.assertTrue(os.path.exists(join("test",file)))
        with open(join("test", file), 'r') as content_file:
            self.assertEquals(content_file.read(), datafile_content)

    def test_collate_datafile_into_existing(self):
        from mpi_prep import collate_data_file
        file = "test_datafile.csv"
        datafile_content = "ImageNumber,A,B,C,D,E\n1,2,3,4,5,6\n"
        combined_datafile = "ImageNumber,A,B,C,D,E\n1,2,3,4,5,6\n2,2,3,4,5,6\n"
        self.create_testfile(file, datafile_content)
        self.create_collationfile(file, datafile_content)
        collate_data_file("test","content",file)
        self.assertTrue(os.path.exists(join("test",file)))
        with open(join("test", file), 'r') as content_file:
            self.assertEquals(content_file.read(), combined_datafile)

    def test_collate_multiple_image_manifest_into_existing(self):
        from mpi_prep import collate_data_file
        file = "test_datafile.csv"
        datafile_content = "ImageNumber,A,B,C,D,E\n1,2,3,4,5,6\n1,2,3,5,5,6\n2,2,3,4,5,6\n2,2,3,5,5,6\n"
        combined_datafile = "ImageNumber,A,B,C,D,E\n1,2,3,4,5,6\n1,2,3,5,5,6\n2,2,3,4,5,6\n2,2,3,5,5,6\n3,2,3,4,5,6\n3,2,3,5,5,6\n4,2,3,4,5,6\n4,2,3,5,5,6\n"
        self.create_testfile(file, datafile_content)
        self.create_collationfile(file, datafile_content)
        collate_data_file("test","content",file)
        self.assertTrue(os.path.exists(join("test",file)))
        with open(join("test", file), 'r') as content_file:
            self.assertEquals(content_file.read(), combined_datafile)

    def test_full_collation_machinery(self):
        #the only integration test in this unit test suite.
        from mpi_prep import collate

        imagefile = "test_image.jpg"

        manifestfile = "test_manifest.csv"
        manifest_content = "A,B,C,ImageNumber,Group_Index,F\n1,2,3,1,1,5\n1,2,3,2,2,5\n"
        combined_manifest = "A,B,C,ImageNumber,Group_Index,F\n1,2,3,1,1,5\n1,2,3,2,2,5\n1,2,3,3,3,5\n1,2,3,4,4,5\n"

        datafile = "test_datafile.csv"
        datafile_content = "ImageNumber,A,B,C,D,E\n1,2,3,4,5,6\n1,2,3,5,5,6\n2,2,3,4,5,6\n2,2,3,5,5,6\n"
        combined_datafile = "ImageNumber,A,B,C,D,E\n1,2,3,4,5,6\n1,2,3,5,5,6\n2,2,3,4,5,6\n2,2,3,5,5,6\n3,2,3,4,5,6\n3,2,3,5,5,6\n4,2,3,4,5,6\n4,2,3,5,5,6\n"

        self.create_testfile(manifestfile, manifest_content)
        self.create_testfile(datafile, datafile_content)

        self.create_collationfile(imagefile, "")
        self.create_collationfile(manifestfile, manifest_content)
        self.create_collationfile(datafile, datafile_content)

        collate("test", "content", "content")

        #check the file results.
        self.assertTrue(os.path.exists(join("test", imagefile)))
        with open(join("test", manifestfile), 'r') as result_manifest_file:
            self.assertEquals(result_manifest_file.read(), combined_manifest)
        with open(join("test", datafile), 'r') as result_data_file:
            self.assertEquals(result_data_file.read(), combined_datafile)
        #check that the original content directory is gone.
        self.assertFalse(os.path.exists(join("test", "content")))

doctest.testmod(mpi_prep, verbose=True)
unittest.main()
