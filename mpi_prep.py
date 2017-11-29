
from __future__ import print_function
import os
import csv
import shutil
import StringIO
import string
import sys
from os import listdir
from os.path import isfile, join
from filelock import FileLock
from shutil import copyfile

#input_dir    = os.environ['INPUT_DIR']
#finished_job = os.environ['job']

def fileclasses(f_list, suffix):
    """
        fileclasses(file_list, suffuix) returns an array of all file name classes
        which match the given suffix.

        >>> fileclasses(["test_image.jpg"], ".jpg")
        ['test_image']
    """
    l = len(suffix)
    arr = [filename[0:-l] for filename in f_list if filename.endswith(suffix)]
    arr.sort()
    return arr

def assembleclass(images_path, scratch_path, classname):
    os.makedirs(join(scratch_path, classname))
    for file in listdir(images_path):
        if os.path.isfile(join(images_path, file)) and file.startswith(classname):
            os.symlink(join(os.path.abspath(images_path),file), join(scratch_path, classname, file))

def isimagefile(f):
    """
        isimage(filename) returns true if we think this filename represents an
        image.  Should support most image filename suffixes.

        >>> isimagefile("test_image.jpg")
        True
    """
    lf = f.lower()
    return ('.jpg' in lf) or ('.png' in lf) or ('.tif' in lf) or ('.tiff' in lf)

def first_line(f):
    """
      first_line(filename) returns the first line of a particular file.

      >>> first_line(StringIO.StringIO("line 1\\nline 2\\n"))
      'line 1'
    """
    return f.readline().strip()

def last_line(f):
    """
      last_line(filename) returns the last line of a particular file.

      >>> last_line(StringIO.StringIO("line 1\\nline 2\\n"))
      'line 2'
    """
    #gets the last line of a file, presumes file f is openend.
    f.seek(0, os.SEEK_END)  #seek to the end
    while f.read(1) != b"\n":   # Until EOL is found...
        f.seek(-2, os.SEEK_CUR) # ...jump back the read byte plus one more.
    return f.readline().strip() # Read last line, and strip


def isimagemanifest(f):
    """
        isimagemanifest(filename) returns true if we think this filename represents
        an image manifest.
    """
    if not('.csv' in f):
        return False
    with open(f, "r") as file:
        return get_valueat(first_line(file),0) != "ImageNumber"

def isdatafile(f):
    """
        isdatafile(filename) returns true if we think this filename represents
        a data file.
    """
    if not('.csv' in f):
        return False
    with open(f, "r") as file:
        return get_valueat(first_line(file),0) == "ImageNumber"

def get_column(f, val):
    """
      get_column(filename, column) gets the column index for a column identifier.

      >>> get_column(StringIO.StringIO("A,B,C\\n1,2,3\\n"), "B")
      1
    """
    f.seek(0, os.SEEK_SET)                  #seek to the start of the file, first line should have file headings.
    return csv.reader(f).next().index(val)  #use the builtin csv package to help handle strange cases.

def get_valueat(rowstr, idx):
    """
      get_valueat(row, idx) gets the column value in a row.  Note.  This outputs
      as a string, even if the value is an integer.

      >>> get_valueat("A,1,C", 1)
      '1'
    """
    return csv.reader([rowstr]).next()[idx]

def substitute_column(rowstr, idx, newval):
    """
      substitute_column(row, idx, val) replaces column value at idx in a row,
      with passed value newval

      >>> substitute_column("A,1,C", 1, "B")
      'A,B,C'
    """
    dst = StringIO.StringIO()
    arr = csv.reader([rowstr]).next()
    arr[idx] = newval
    csv.writer(dst).writerow(arr)
    return dst.getvalue().strip()

def find_and_follow_symlink(directory):
    for f in listdir(directory):
        if isimagefile(f):
            true_path = os.readlink(join(directory,f))
            return os.path.dirname(true_path)

def substitute_directory(rowstr, directory):
    dst = StringIO.StringIO()
    arr = csv.reader([rowstr]).next()
    for idx in range(0, len(arr)):
        if arr[idx].startswith(directory):
            #find an image file in this directory
            arr[idx] = find_and_follow_symlink(directory)
        if arr[idx].startswith("file:" + directory):
            filename = arr[idx]
            arr[idx] = "file:" + join(find_and_follow_symlink(os.path.dirname(filename[5:])), os.path.basename(filename))
    csv.writer(dst).writerow(arr)
    return dst.getvalue().strip()

def collate_image_file(jobsdir, job_to_collate, image_file):
    os.rename(join(jobsdir, job_to_collate, image_file), join(jobsdir, image_file))

def transfer_image_manifest(src_path, dst_path, images_dir):
    with open(src_path, "r") as src_file:
        with open(dst_path, "w") as dst_file:
            for line in src_file.readlines():
                substituted_file_row = substitute_directory(line, images_dir)
                dst_file.write(substituted_file_row)
                dst_file.write("\n")

def collate_image_manifest(jobsdir, job_to_collate, image_file, images_dir):
    #check if the image manifest file exists in the jobsdir directory.
    if os.path.exists(join(jobsdir, image_file)):
        #do a simple append.
        with open(join(jobsdir, image_file), "r+") as dstfile:
            with open(join(jobsdir, job_to_collate, image_file), "r") as srcfile:
                #handle imagenumber variable.
                imagenumber_col = get_column(srcfile, "ImageNumber")
                imagenumber_index_delta = int(get_valueat(last_line(dstfile), imagenumber_col))
                srcfile.seek(0,os.SEEK_SET)

                groupindex_col = get_column(srcfile, "Group_Index")
                groupindex_delta = int(get_valueat(last_line(dstfile), groupindex_col))
                srcfile.seek(0,os.SEEK_SET)
                #note that srcfile is already at line 2 because of the side
                #effect of target_col
                for line in srcfile.readlines()[1:]:
                    image_index_val = int(get_valueat(line, imagenumber_col)) + imagenumber_index_delta
                    updated_image_index_row = substitute_column(line, imagenumber_col, image_index_val)

                    groupindex_val = int(get_valueat(line, groupindex_col)) + groupindex_delta
                    updated_group_index_row = substitute_column(updated_image_index_row, groupindex_col, groupindex_val)

                    substituted_file_row = substitute_directory(updated_group_index_row, images_dir)
                    dstfile.write(substituted_file_row)
                    dstfile.write("\n")
    else:
        #copy the file over to seed the jobsdir.)
        transfer_image_manifest(join(jobsdir,job_to_collate, image_file), join(jobsdir, image_file), images_dir)

def collate_data_file(jobsdir, job_to_collate, data_file):
    #check if the parent data file exists in the jobsdir directory.
    if os.path.exists(join(jobsdir, data_file)):
        #do a simple append.  TODO: consider merging this with above file.
        with open(join(jobsdir, data_file), "r+") as dstfile:
            with open(join(jobsdir, job_to_collate, data_file), "r") as srcfile:
                index_delta = int(get_valueat(last_line(dstfile), 0))
                srcfile.seek(0,os.SEEK_SET)
                for line in srcfile.readlines()[1:]:
                    new_val = int(get_valueat(line, 0)) + index_delta
                    finalized_row = substitute_column(line, 0, new_val)
                    dstfile.write(finalized_row)
                    dstfile.write("\n")
    else:
        #copy the file over to seed the jobsdir.)
        copyfile(join(jobsdir,job_to_collate, data_file), join(jobsdir, data_file))

def collate(jobsdir, job_to_collate, images_dir):
    collatedir = join(jobsdir, job_to_collate)
    for f in listdir(collatedir):
        fullpath = join(collatedir, f)
        if isimagefile(fullpath):
            collate_image_file(jobsdir, job_to_collate, f)
        elif isimagemanifest(fullpath):
            collate_image_manifest(jobsdir, job_to_collate, f, images_dir)
        elif isdatafile(fullpath):
            collate_data_file(jobsdir, job_to_collate, f)
    shutil.rmtree(collatedir)

def find_next_job(job_list, last_job):
    if last_job == "":
        return job_list[0]
    else:
        last_job_index = job_list.index(last_job)
        if last_job_index + 1 == len(job_list):
            return "done"
        else:
            return job_list[job_list.index(last_job) + 1]

def handle_cache(job_list, output_dir, unstaged_jobs, completed_job, images_dir):
    unstaged_jobs.append(completed_job)
    next_job = completed_job
    while completed_job in unstaged_jobs:
        collate(output_dir, next_job, images_dir)
        #clear out the next job directory from the scratch directory
        shutil.rmtree(join(scratch_dir, next_job))
        #remove it from the list(so we can write it back to the file.)
        unstaged_jobs.remove(next_job)

        if next_job == job_list[-1]:
            break
        else:
            next_job = find_next_job(job_list, next_job)

    with open(join(scratch_dir, "UNSTAGED_JOBS"), "w") as file:
        file.write(string.join(unstaged_jobs, "\n"))
    return next_job

def prepare_job(images_dir, scratch_dir, output_dir, job_name):
    if (job_name != "done"):
        #create directory with symlinks into the assemblage.
        assembleclass(images_dir, scratch_dir, job_name)
    #take care of reporting:  send the next fetched file to stdout
    #and also send it to the MPI_STATUS file.
    print(job_name)
    with open(join(scratch_dir, "MPI_STATUS"), "a") as file:
        file.write(job_name + "\n")

def handle_mpi_cycling(scratch_dir, output_dir, file_suffix, job_list, completed_job):
    #an MPI_STATUS file exists.

    unstaged_jobs = []
    unstaged_file = join(scratch_dir, "UNSTAGED_JOBS")
    with open(unstaged_file, "r") as file:
        unstaged_jobs = file.readlines()

    output_directories = [dir for dir in listdir(output_dir) if os.path.isdir(join(output_dir, dir))]

    if not (completed_job in output_directories):
        #this should never happen.
        print("error, completed job not found in the output directories.")
        exit(1)

    #next fetch the NEXT job.
    status_file = join(scratch_dir, "MPI_STATUS")
    with open(status_file, "r") as mpistatus:
        last_completed, last_fetched = map(lambda line: line.strip(), mpistatus.readlines())

    if completed_job == find_next_job(job_list, last_completed):
        last_completed = handle_cache(job_list, output_dir, unstaged_jobs, completed_job, join(scratch_dir, completed_job))
    else:
        #TODO: check the validity of this code.
        with open(unstaged_file, "a") as file:
            file.write(completed_job + "\n")

    with open(status_file, "w") as mpistatus:
        mpistatus.write(completed_job + "\n")

    if last_fetched != job_list[-1]:
        return find_next_job(job_list, last_fetched)
    else:
        return "done"

def create_status_files(scratch_dir):
    with open(join(scratch_dir, "MPI_STATUS"), "w") as file:
        file.write("\n")
    with open(join(scratch_dir, "UNSTAGED_JOBS"), "w") as file:
        file.write("")

if __name__ == "__main__":
    images_dir = sys.argv[1]
    scratch_dir = sys.argv[2]
    output_dir = sys.argv[3]
    file_suffix = sys.argv[4]
    completed_job = sys.argv[5] if len(sys.argv) == 6 else ""
    #next put a semaphore around the process
    file_lock = join(scratch_dir, "file_lock")
    with FileLock(file_lock):
        job_list = fileclasses(listdir(images_dir), file_suffix)
        next_job = ""
        if (completed_job == ""):
            create_status_files(scratch_dir)
            next_job = job_list[0]
        else:
            next_job = handle_mpi_cycling(scratch_dir, output_dir, file_suffix, job_list, completed_job)
        prepare_job(images_dir, scratch_dir, output_dir, next_job)
