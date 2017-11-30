
from __future__ import print_function
import os
import csv
import shutil
import StringIO
import string
import sys
import re
from os import listdir
from os.path import isfile, join
from filelock import FileLock
from shutil import copyfile

#input_dir    = os.environ['INPUT_DIR']
#finished_job = os.environ['job']

def trimby(filename, regex):
    matchstr = re.search(regex, filename).group(0)
    l = len(matchstr)
    return filename[:-l]

def fileclasses(f_list, matchdesc):
    """
        fileclasses(file_list, suffix) returns an array of all file name classes
        which match the given suffix.

        fileclasses(file_list, regexstring) returns an array of all file name classes
        which match the given regexstring

        >>> fileclasses(["test_image.jpg"], ".jpg")
        ['test_image']

        >>> fileclasses(["abc_aw123.jpg"], "r/aw(.*).jpg/")
        ['abc_']
    """
    if matchdesc.startswith("r/"):
        if not matchdesc.endswith("/"):
            sys.error.write("error: bad regex suffix definition\n")
            exit(1)
        regex = re.compile(matchdesc[2:-1])
        arr = [trimby(filename, regex) for filename in f_list if re.search(regex, filename)]
        arr.sort()
        return arr
    else:
        l = len(matchdesc)
        arr = [filename[0:-l] for filename in f_list if filename.endswith(matchdesc)]
        arr.sort()
        return arr

def assembleclass(images_path, scratch_path, classname):
    if os.path.isdir(join(images_path, classname)):
        os.symlink(join(os.path.abspath(images_path), classname), join(scratch_path, classname))
    else:
        os.makedirs(join(scratch_path, classname))
        for file in listdir(images_path):
            #xml files get copied "no matter what"
            if file.endswith(".xml"):
                os.symlink(join(os.path.abspath(images_path),file), join(scratch_path, classname, file))
            #image files get copied if their path matches the classname.
            if isimagefile(file):
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
    return any(map(lambda ext: lf.endswith(ext), ['.jpg', '.png', '.tif','.tiff']))

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

def isexperimentfile(f):
    """
        isexperimentfile(filename) returns true if we think this filename represents
        an experiment file.
    """
    return f.endswith("Experiment.csv")

def isimagemanifest(f):
    """
        isimagemanifest(filename) returns true if we think this filename represents
        an image manifest.
    """
    if not('.csv' in f):
        return False
    with open(f, "r") as file:
        return not(get_valueat(first_line(file),0) in ["ImageNumber", "Image"])

def isdatafile(f):
    """
        isdatafile(filename) returns true if we think this filename represents
        a data file.
    """
    if not('.csv' in f):
        return False
    with open(f, "r") as file:
        return get_valueat(first_line(file),0) in ["ImageNumber", "Image"]

def get_column(f, val):
    """
      get_column(filename, column) gets the column index for a column identifier.
      returns -1 if the column doesn't exist.

      >>> get_column(StringIO.StringIO("A,B,C\\n1,2,3\\n"), "B")
      1
      >>> get_column(StringIO.StringIO("A,B,C\\n1,2,3\\n"), "Q")
      -1
    """
    f.seek(0, os.SEEK_SET)          #seek to the start of the file, first line should have file headings.
    datalist = csv.reader(f).next() #use the builtin csv package to help handle strange cases.
    return datalist.index(val) if val in datalist else -1

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


def collate_experiment_file(jobsdir, job_to_collate, experiment_file):
    if not os.path.exists(join(jobsdir, experiment_file)):
        os.rename(join(jobsdir, job_to_collate, experiment_file), join(jobsdir, experiment_file))

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
                if (imagenumber_col > 0):
                    imagenumber_index_delta = int(get_valueat(last_line(dstfile), imagenumber_col))
                srcfile.seek(0,os.SEEK_SET)

                groupindex_col = get_column(srcfile, "Group_Index")
                if (groupindex_col > 0):
                    groupindex_delta = int(get_valueat(last_line(dstfile), groupindex_col))
                srcfile.seek(0,os.SEEK_SET)
                #note that srcfile is already at line 2 because of the side
                #effect of target_col
                for line in srcfile.readlines()[1:]:
                    if (imagenumber_col > 0):
                        image_index_val = int(get_valueat(line, imagenumber_col)) + imagenumber_index_delta
                        updated_image_index_row = substitute_column(line, imagenumber_col, image_index_val)
                    else:
                        updated_image_index_row = line

                    if (groupindex_col > 0):
                        groupindex_val = int(get_valueat(line, groupindex_col)) + groupindex_delta
                        updated_group_index_row = substitute_column(updated_image_index_row, groupindex_col, groupindex_val)
                    else:
                        updated_group_index_row = updated_image_index_row

                    substituted_file_row = substitute_directory(updated_group_index_row, images_dir)
                    dstfile.write(substituted_file_row)
                    dstfile.write("\n")
    else:
        #copy the file over to seed the jobsdir.)
        transfer_image_manifest(join(jobsdir,job_to_collate, image_file), join(jobsdir, image_file), images_dir)

def is_number(s):
    """ Returns True is string is a number. """
    return s.replace('.','',1).isdigit()

def collate_data_file(jobsdir, job_to_collate, data_file):
    if os.path.exists(join(jobsdir, data_file)):
        #do a simple append.  TODO: consider merging this with above file.
        with open(join(jobsdir, data_file), "r+") as dstfile:
            with open(join(jobsdir, job_to_collate, data_file), "r") as srcfile:
                index_delta = int(get_valueat(last_line(dstfile), 0))
                srcfile.seek(0,os.SEEK_SET)
                for line in srcfile.readlines()[1:]:
                    if not is_number(get_valueat(line, 0)):
                        continue
                    new_val = int(get_valueat(line, 0)) + index_delta
                    finalized_row = substitute_column(line, 0, new_val)
                    dstfile.write(finalized_row)
                    dstfile.write("\n")
    else:
        #copy the file over to seed the jobsdir.)
        copyfile(join(jobsdir,job_to_collate, data_file), join(jobsdir, data_file))

def collate(jobsdir, job_to_collate, images_dir):
    collatedir = join(jobsdir, job_to_collate)
    if os.path.isdir(join(collatedir, job_to_collate)):
        os.rename(collatedir, join(jobsdir, "_tmp"))
        os.rename(join(jobsdir, "_tmp", job_to_collate), join(jobsdir, job_to_collate))
        shutil.rmtree(join(jobsdir, "_tmp"))
    else:
        for f in listdir(collatedir):
            fullpath = join(collatedir, f)
            if isimagefile(fullpath):
                #sys.stderr.write("image file: " + f)
                collate_image_file(jobsdir, job_to_collate, f)
            elif isexperimentfile(fullpath):
                #sys.stderr.write("experiment file: " + f)
                collate_experiment_file(jobsdir, job_to_collate, f)
            elif isimagemanifest(fullpath):
                #sys.stderr.write("image manifest file: " + f)
                collate_image_manifest(jobsdir, job_to_collate, f, images_dir)
            elif isdatafile(fullpath):
                #sys.stderr.write("data file: " + f)
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
        if os.path.islink(join(scratch_dir, next_job)):
            os.remove(join(scratch_dir, next_job))
        else:
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
        images_contents = listdir(images_dir)

        if all([os.path.isdir(join(images_dir, file)) for file in images_contents]):
            images_contents.sort()
            job_list = images_contents
        else:
            job_list = fileclasses(images_contents, file_suffix)

        next_job = ""
        if (completed_job == ""):
            create_status_files(scratch_dir)
            next_job = job_list[0]
        else:
            next_job = handle_mpi_cycling(scratch_dir, output_dir, file_suffix, job_list, completed_job)
        prepare_job(images_dir, scratch_dir, output_dir, next_job)
