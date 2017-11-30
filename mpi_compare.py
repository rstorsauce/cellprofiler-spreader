
import sys
import csv
import re
import hashlib
from os.path import join
from os.path import isdir
from os import listdir

std_dir = sys.argv[1]
mpi_dir = sys.argv[2]

def header_exceptions(header):
    if header in []:
        return True
    if header.startswith("ExecutionTime"):
        return True
    if header.startswith("ImageSet"):
        return True
    return False

def row_exceptions(row):
    if row[0] in ["ImageSet_Zip_Dictionary", "Run_Timestamp"]:
        return True
    return False

def is_inconsistent(std,mpi):
    if std == mpi:
        return False
    if re.sub(r'std','mpi',std) == mpi:
        return False
    return True

def comparerow(std_row, mpi_row, header, f):
    if len(std_row) != len(mpi_row):
        print("error, csv row " + std_row + " in file " + f +" has mismatching length \n")
        exit(1)
    if row_exceptions(std_row):
        return
    for idx in range(0, len(std_row)):
        if not header_exceptions(header[idx]):
            if is_inconsistent(std_row[idx], mpi_row[idx]):
                print("error, column " + header[idx] + " mismatches in file " + f + ":\n")
                print("std value: " + std_row[idx] + "\n")
                print("mpi value: " + mpi_row[idx] + "\n")
                exit(1)


def comparecsv(std_path, mpi_path, f):
    with open(std_path, "r") as std_file:
        with open(mpi_path, "r") as mpi_file:
            std_csv = [row for row in csv.reader(std_file)]
            mpi_csv = [row for row in csv.reader(mpi_file)]

            if len(std_csv) != len(mpi_csv):
                print("error, csv files have mismatching length: " + f + "\n")
                exit(1)

            if std_csv[0] != mpi_csv[0]:
                print("error, csv files have mismatching header: " + f + "\n")
                exit(1)

            header = std_csv[0]
            for idx in range(1, len(std_csv)):
                std_row = std_csv[idx]
                mpi_row = mpi_csv[idx]
                comparerow(std_row, mpi_row, header, f)


for f in listdir(std_dir):
    if not f in listdir(mpi_dir):
        print("error, file " + f + " not in mpi directory!\n")
        exit(1)

for f in listdir(mpi_dir):
    if not f in listdir(std_dir):
        print("error, extra file " + f + " in mpi directory!\n")
        exit(1)

for f in listdir(std_dir):
    if f.endswith(".csv"):
        comparecsv(join(std_dir, f), join(mpi_dir, f), f)
    else:
        if isdir(join(std_dir, f)):
            continue
        expected_md5 = ""
        #check that the checksums of the two files are the same.
        with open(join(std_dir, f)) as file_to_check:
            data = file_to_check.read()
            expected_md5 = hashlib.md5(data).hexdigest()
        with open(join(std_dir, f)) as file_to_check:
            data = file_to_check.read()
            if expected_md5 != hashlib.md5(data).hexdigest():
                print("error, file " + f + " inconsistent between mpi and std\n")
                exit(1)
