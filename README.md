mpi_prep.py
===========

a script that adapts cellprofiler to run as MPI ('without actual mpi').  there
is some overhead penalty to the process of repeatedly loading and unloading the
runtime, but it's our belief that this penalty is minor.  Statistics to come.


using mpi_prep.py
-----------------

python mpi_prep.py source_images_dir scratch_dir output_dir file_suffix [last_finished_job]

uses [last_finished_job] collates existing subdirectories of `output_dir` and
merges them into the main directory.  These will be correctly threaded
sequentially.  During this process, scratch subdirectories will be cleared out.

looks through `source_images_dir`, and finds the first unprocessed image
that matches `file_suffix`.  copies these images into `scratch_dir`

creates a subdirectory in `output_dir` that will contain the output from
processing this the image and associated images.

the output of the program is the label of the currenly run job (to be passed
  back into `last_finished_job`, or, if done, 'done'

two helper files are created in the `scratch_dir`.

1. MPI_STATUS

stores the last fetched file.

2. UNSTAGED_JOBS

this file contains a list of all jobs that haven't been collated but are blocking
because there is an unfinished job that needs to be collated before it.
