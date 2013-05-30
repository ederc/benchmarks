#!/usr/bin/python

import sys
import fnmatch
import os
import shutil
import argparse
from argparse import RawTextHelpFormatter
import time
import math
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import pylab as pl
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

currentdir  = os.getcwd()

parser = argparse.ArgumentParser(description='\
',
formatter_class=RawTextHelpFormatter)
parser.add_argument( '--folder1', required=True,
    help='1st folder')
parser.add_argument( '--folder2', required=True,
    help='2nd folder')

args = parser.parse_args()


# get filenames
benched = list()
for f in os.listdir(args.folder1):
  if fnmatch.fnmatch(f,'test-*'):
    benched.append(f)

for i in range (0,len(benched)):
  if not os.path.exists(benched[i]):
    os.makedirs(benched[i])
  srcfolder1 = args.folder1+'/'+benched[i]
  srcfolder2 = args.folder2+'/'+benched[i]
  foldernew = benched[i]
  benched[i]  = benched[i].replace('test','bench')
  shutil.copy2(srcfolder1+'/'+benched[i],foldernew+'/'+benched[i])
  os.system('cat '+srcfolder2+'/'+benched[i]+' >> '+foldernew+'/'+benched[i])
