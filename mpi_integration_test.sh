#!/bin/sh

set -e

#mpi_integration_test.sh -- performs an integration test on the tool.
#requires cellprofiler to be installed on the base system
#requires access to /tmp
#should be executed from the base cellprofiler-mpi-tool directory.

#before proceeding, make sure that the directory exists.
if [ ! -d "testsamples/$1" ]; then
  echo "failure: test directory not found."
  exit 1
fi

if [ ! -x "testsamples/$1/expand.sh" ]; then
  echo "failure: expand script not found."
  exit 1
fi

#preclean in case we started from a dirty state.
if [ -d /tmp/cellprofiler-test ]; then
  rm -rf /tmp/cellprofiler-test
fi

mpi_prep_dir=$(pwd)
cd testsamples

mkdir -p /tmp/cellprofiler-test/

std_dir="/tmp/cellprofiler-test/$1-std"
mpi_dir="/tmp/cellprofiler-test/$1-mpi"

#make two copies, one in "mpi mode", and one in "not mpi mode"
cp -r "$1" "$std_dir"
cp -r "$1" "$mpi_dir"

#the directories should contain an "expand.sh" file which makes 4 copies of the
#files.

cd "$std_dir"
_=$(./expand.sh)
cd "$mpi_dir"
mpisuffix=$(./expand.sh)

#make two output directories
mkdir "/tmp/cellprofiler-test/output-std"
mkdir "/tmp/cellprofiler-test/output-mpi"

#run the standard version of cellprofiler.
cd "$std_dir"
cellprofiler -c -p "$1.cppipe" -i images -o /tmp/cellprofiler-test/output-std

cd "$mpi_dir"
output_base="/tmp/cellprofiler-test/output-mpi"
#run the "mpi" version of cellprofiler.
d1=`python "$mpi_prep_dir/mpi_prep.py" "$mpi_dir/images" "/tmp/cellprofiler-test" "$output_base" "$mpisuffix"`
cellprofiler -c -p "$1.cppipe" -i "/tmp/cellprofiler-test/$d1" -o "/tmp/cellprofiler-test/output-mpi/$d1"
d2=`python "$mpi_prep_dir/mpi_prep.py" "$mpi_dir/images" "/tmp/cellprofiler-test" "$output_base" "$mpisuffix" "$d1"`
cellprofiler -c -p "$1.cppipe" -i "/tmp/cellprofiler-test/$d2" -o "/tmp/cellprofiler-test/output-mpi/$d2"
d3=`python "$mpi_prep_dir/mpi_prep.py" "$mpi_dir/images" "/tmp/cellprofiler-test" "$output_base" "$mpisuffix" "$d2"`
cellprofiler -c -p "$1.cppipe" -i "/tmp/cellprofiler-test/$d3" -o "/tmp/cellprofiler-test/output-mpi/$d3"
d4=`python "$mpi_prep_dir/mpi_prep.py" "$mpi_dir/images" "/tmp/cellprofiler-test" "$output_base" "$mpisuffix" "$d3"`
cellprofiler -c -p "$1.cppipe" -i "/tmp/cellprofiler-test/$d4" -o "/tmp/cellprofiler-test/output-mpi/$d4"
d5=`python "$mpi_prep_dir/mpi_prep.py" "$mpi_dir/images" "/tmp/cellprofiler-test" "$output_base" "$mpisuffix" "$d4"`

cd "$mpi_prep_dir"
python mpi_compare.py /tmp/cellprofiler-test/output-std /tmp/cellprofiler-test/output-mpi
