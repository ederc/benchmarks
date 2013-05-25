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
from matplotlib.backends.backend_pdf import PdfPages

def cmp_to_key(mycmp):
  'Convert a cmp= function into a key= function'
  class K(object):
    def __init__(self, obj, *args):
      self.obj = obj
    def __lt__(self, other):
      return mycmp(self.obj, other.obj) < 0
    def __gt__(self, other):
      return mycmp(self.obj, other.obj) > 0
    def __eq__(self, other):
      return mycmp(self.obj, other.obj) == 0
    def __le__(self, other):
      return mycmp(self.obj, other.obj) <= 0  
    def __ge__(self, other):
      return mycmp(self.obj, other.obj) >= 0
    def __ne__(self, other):
      return mycmp(self.obj, other.obj) != 0
  return K

def sortbenched(a, b):
  cmpvalsa = a.split('-')
  cmpvalsb = b.split('-')
  if int(cmpvalsa[3]) == int(cmpvalsb[3]):
    return int(cmpvalsa[4]) - int(cmpvalsb[4])
  else:
    return int(cmpvalsa[3]) - int(cmpvalsb[3])

currentdir = os.getcwd()

parser = argparse.ArgumentParser(description='\
Generates two random matrices a and b with either float\n\
or uint16 entries. these matrices are then multiplied,\n\
thus it is enough to predefine #rows of a, #cols of a\n\
and #cols of b. The multiplication is performed in various\n\
combinations of the f4rt dense matrix multiplication\n\
implementation. afterwards the stored results are visualized.',
formatter_class=RawTextHelpFormatter)
parser.add_argument('-p', '--plot', action='store_true',
    help='plotting of results? (default=0)')
parser.add_argument('-s', '--matrixsize', default=1,
    help='matrix size in files to search for')

args = parser.parse_args()

benched = list()

for file in os.listdir('.'):
  if fnmatch.fnmatch(file, 'test-'+args.matrixsize+'*'):
    benched.append(file)

benched.sort(key=cmp_to_key(sortbenched))

methods = list()
methodsReal = list()

for i in range(0,len(benched)):
  methods.append(i)
  tmp = benched[i].replace('test-'+args.matrixsize+'-'+args.matrixsize+'-','')
  tmp2 = tmp.split('-')
  methodsReal.append('B'+tmp2[0]+'-L'+tmp2[1])

# lists for all methods we have, those are lists of lists:
# e.g. time_series[i] is a list of len(threads) elements of the timings
# of methods[i]. 
time_series = list()
gflops_series = list()

for i in range(0,len(methodsReal)):
  time_series.append(list())
  gflops_series.append(list())



##############################################
# plotting part of the script
##############################################

layoutSizes = list()
blockSizes  = list()
matrixSizes = list()
file_names  = list()
lines       = list()

if args.plot:
  for i in range(0,len(methodsReal)):
    tmp = benched[i].replace('test','')
    bench_file = benched[i]+'/bench'+tmp
    file_names.append(bench_file)

    file_name = file_names[i]
    # read lines of the benchmark files
    f = open(file_name)
    lines.append(f.readlines())
    f.close()

  # get information about the dimension, #threads, blocksizes and layouts
  dimensions = lines[0][0].strip().replace(' ','').split(',')
  
  # second line are the thread settings used
  plot_threads = lines[0][1].strip().replace(' ','').split(',')

  # get threads for plot, stored in the first line of bench file
  #plot_threads = f.readline().strip().replace(' ','').split(',')
  # for compatibility to the other scripts just store this again
  threads = plot_threads
  threads = list(map(lambda x: int(x) - 1, threads))


  for i in range(0,len(lines)):
    for l in lines[i]:
      tmp = i
      if l.find('avg_real_calu_time:') != -1:
        ltmp = l.split(',')
        time_series[tmp].append(\
            ltmp[0].replace('avg_real_calu_time:','').strip())
        gflops_series[tmp].append(\
            float(ltmp[1].replace('avg_Gflops:','').replace('/s','').replace('inf','-1').strip()))

  #plot this data

  #line style, sequential method only if start_threads == 1
  stride = 1
  coloring =\
  [\
  '#0099cc','#33cc00','#ff1b54','#0033cc','#9900cc','#800020',\
  '#ff4011','#ffbf01','#00144f','#ff1450',\
  '#0099cc','#33cc00','#cc0033','#0033cc','#9900cc','#800020',\
  '#ff4011','#ffbf01','#00144f','#ff1450',\
  '#0099cc','#33cc00','#cc0033','#0033cc','#9900cc','#800020',\
  '#ff4011','#ffbf01','#00144f','#ff1450',\
  '#0099cc','#33cc00','#cc0033','#0033cc','#9900cc','#800020',\
  '#ff4011','#ffbf01','#00144f','#ff1450'\
  ]
  styles = [\
  '-','-','-','-','-','-','-','-','-','-',\
  '--','--','--','--','--','--','--','--','--','--',\
  ':',':',':',':',':',':',':',':',':',':',\
  '-','-','-','-','-','-','-','-','-','-'\
  ]
  markers = [\
  'None','None','None','None','None','None','None','None','None','None',\
  'None','None','None','None','None','None','None','None','None','None',\
  'None','None','None','None','None','None','None','None','None','None',\
  'o','o','o','o','o','o','o','o','o','o'\
  ]

  pp =\
  PdfPages('results-inc-threads-'+str(args.matrixsize)+'-'+str(args.matrixsize)+'.pdf')
  pl.rc('legend',**{'fontsize':5})
  fig = pl.figure()
  ax = fig.add_subplot(111)
  fig.suptitle('Timings: CALU fully-dynamic scheduling w/ MKL', fontsize=10)
  pl.title('Matrix dimensions: '+dimensions[0]+
  ' x '+dimensions[1]+' (B ~ Blocksize, L ~ Layout)', fontsize=8)
  ax.set_xlabel('Number of threads', fontsize=7)

  ax.set_ylabel('Real time in seconds', fontsize=8)

  pl.grid(b=True, which='major', color='k', linewidth=0.3)
  pl.grid(b=True, which='minor', color='k', linewidth=0.1, alpha=0.5)

  ax = pl.gca() 

  group_labels = plot_threads

  #ax.set_xticklabels(group_labels)
  threads_tmp = range(0,len(plot_threads))
  # get right scale for a4 paper size
  scale_tmp = 64 // (len(plot_threads)) 
  threads = range(0,64,scale_tmp)
  tick_lbs = plot_threads
  ax.xaxis.set_ticks(threads)
  ax.xaxis.set_ticklabels(tick_lbs)

  p = [None]*len(methods)
  for i in range(0,len(methods)):
    p[i], = ax.plot(threads[0:len(time_series[i])], time_series[i], c=coloring[i],
        ls=styles[i], marker=markers[i], markersize='4', label=i)
  # set 0 as min value for y and 1 as min value for x (threads)
  #pl.xlim(xmin=1)
  pl.ylim(ymin=0) 
  
  ax.legend((methodsReal),'upper right', shadow=True, fancybox=True)

  # take real time of sequential computation to figure out the 
  # granularity of the yaxis
  tmp_ticks = ax.yaxis.get_majorticklocs()
  granu = tmp_ticks[len(tmp_ticks)-1] // (len(tmp_ticks)-1) // 5
  ax.yaxis.set_minor_locator(MultipleLocator(granu))
  pl.tick_params(axis='both', which='major', labelsize=6)
  pl.tick_params(axis='both', which='minor', labelsize=6)

  #pl.savefig('timings.pdf',format='pdf',papertype='a4',orientation='landscape')
  pl.savefig(pp,format='pdf',papertype='a4',orientation='landscape')


  fig = pl.figure()
  ax = fig.add_subplot(111)
  fig.suptitle('GFLOPS/sec: CALU fully-dynamic scheduling w/ MKL', fontsize=10)
  pl.title('Matrix dimensions: '+dimensions[0]+
  ' x '+dimensions[1]+' (B ~ Blocksize, L ~ Layout)', fontsize=8)
  ax.set_xlabel('Number of threads', fontsize=7)
  ax.set_ylabel('GFLOPS per second', fontsize=8)

  pl.grid(b=True, which='major', color='k', linewidth=0.3)
  pl.grid(b=True, which='minor', color='k', linewidth=0.1, alpha=0.5)

  ax = pl.gca() 

  #ax.set_xticklabels(group_labels)
  threads_tmp = range(0,len(plot_threads))
  # get right scale for a4 paper size
  scale_tmp = 64 // (len(plot_threads)) 
  threads = range(0,64,scale_tmp)
  tick_lbs = plot_threads
  ax.xaxis.set_ticks(threads)
  ax.xaxis.set_ticklabels(tick_lbs)

  p = [None]*len(methods)
  for i in range(0,len(methods)):
    p[i], = ax.plot(threads[0:len(gflops_series[i])], gflops_series[i], c=coloring[i],
        ls=styles[i], marker=markers[i], markersize='4', label=i)
  # set 0 as min value for y and 1 as min value for x (threads)
  #pl.xlim(xmin=1)
  pl.ylim(ymin=0)

  ax.legend((methodsReal),'upper left', shadow=True, fancybox=True)

  # take gflops of best computation to figure out the 
  # granularity of the yaxis
  tmp_ticks = ax.yaxis.get_majorticklocs()
  # note that here "abs()" is needed since if computations are too fast we
  # set GFLOPS to -1 instead of infinity. Since the MultipleLocator must
  # be set to a positive integer value, we have to take care of this case.
  granu = abs(tmp_ticks[len(tmp_ticks)-1]) // (len(tmp_ticks)-1) // 5
  ax.yaxis.set_minor_locator(MultipleLocator(granu))

  pl.tick_params(axis='both', which='major', labelsize=6)
  pl.tick_params(axis='both', which='minor', labelsize=6)

  #pl.savefig('gflops.pdf',format='pdf',papertype='a4',orientation='landscape')
  pl.savefig(pp,format='pdf',papertype='a4',orientation='landscape')
  pp.close()
