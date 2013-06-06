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
  if int(cmpvalsa[1]) == int(cmpvalsb[1]):
    if int(cmpvalsa[3]) == int(cmpvalsb[3]):
      return int(cmpvalsa[4]) - int(cmpvalsb[4])
    else:
      return int(cmpvalsa[3]) - int(cmpvalsb[3])
  else:
    return int(cmpvalsa[1]) - int(cmpvalsb[1])

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
parser.add_argument('-t', '--threads', default=1,
    help='number of threads in files to search for')

args = parser.parse_args()

benched = list()
benchedmkl = list()

if int(args.matrixsize) != 1:
  for file in os.listdir('.'):
    if fnmatch.fnmatch(file, 'test-'+args.matrixsize+'*'):
      benched.append(file)
else:
  for file in os.listdir('.'):
    if fnmatch.fnmatch(file, 'test-*'):
      benched.append(file)


print(benched)

benched.sort(key=cmp_to_key(sortbenched))

methods     = list()
methodsReal = list()
rowSizes    = list()
colSizes    = list()
layoutSizes = list()
blockSizes  = list()
matrixSizes = list()
file_names  = list()
lines       = list()

# lists for all methods we have, those are lists of lists:
# e.g. time_series[i] is a list of len(threads) elements of the timings
# of methods[i]. 
plot_data     = list()
time_series   = list()
gflops_series = list()

for i in range(0,len(benched)):
  methods.append(i)
  tmp = benched[i].split('-')
  tmp2 = 'B'+tmp[-2]+'-L'+tmp[-1]
  if tmp2 not in methodsReal:
    methodsReal.append('B'+tmp[-2]+'-L'+tmp[-1])
  if tmp[1] not in rowSizes:
    rowSizes.append(tmp[1])
  if tmp[2] not in colSizes:
    colSizes.append(tmp[2])

for i in range(0,len(methodsReal)+1):
  time_series.append(list())
  gflops_series.append(list())



##############################################
# plotting part of the script
##############################################

if args.plot:
  for i in range(0,len(benched)):
    tmp = benched[i].replace('test','')
    bench_file = benched[i]+'/bench'+tmp
    file_names.append(bench_file)

    file_name = file_names[i]
    # read lines of the benchmark files
    print(file_name)
    f = open(file_name)
    lines.append(f.readlines())
    f.close()

  # get information about the dimension, #threads, blocksizes and layouts
  dimensions = lines[0][0].strip().replace(' ','').split(',')

  # second line are the thread settings used
  plot_threads = lines[0][1].strip().replace(' ','').split(',')
  
  if int(args.matrixsize) != 1:
    plot_data = plot_threads
  else:
    for i in range(0,len(rowSizes)):
      plot_data.append(str(rowSizes[i]+'/'+str(colSizes[i])))
    threadidx = plot_threads.index(str(args.threads))

  data = plot_data
  #data = list(map(lambda x: int(x) - 1, data))

  print(len(methodsReal))
  print(len(lines))
  print(len(time_series))
  print(len(gflops_series))
  nbr = int(len(lines)) // int(len(methodsReal))
  for i in range(0,nbr):
    for j in range(0,len(methodsReal)):
      tmp = i*len(methodsReal)+j
      if int(args.matrixsize) != 1:
        for l in lines[tmp]:
          if l.find('avg_real_calu_time:') != -1:
            ltmp = l.split(',')
            time_series[j].append(\
                ltmp[0].replace('avg_real_calu_time:','').strip())
            gflops_series[j].append(\
                float(ltmp[1].replace('avg_Gflops:','').replace('/s','').replace('inf','-1').strip()))
      else:
        ctr = 0
        for l in lines[tmp]:
          if l.find('avg_real_calu_time:') != -1:
            if ctr == threadidx:
              ltmp = l.split(',')
              time_series[j].append(\
                  ltmp[0].replace('avg_real_calu_time:','').strip())
              gflops_series[j].append(\
                  float(ltmp[1].replace('avg_Gflops:','').replace('/s','').replace('inf','-1').strip()))
            ctr = ctr + 1

  # start mkl plotting stuff
  if int(args.matrixsize) != 1:
    for file in os.listdir('mkl/'):
      if fnmatch.fnmatch(file, 'test-'+args.matrixsize+'*'):
        benchedmkl.append(file)
  else:
    for file in os.listdir('mkl/'):
      if fnmatch.fnmatch(file, 'test-*'):
        benchedmkl.append(file)

  benchedmkl.sort(key=cmp_to_key(sortbenched))
  print(benchedmkl)

  for i in range(0,len(benchedmkl)):
    if 'MKL-11.0.2.146' not in methodsReal:
      methods.append(i)
      methodsReal.append('MKL-11.0.2.146')
    
  print('----')
  print(len(benchedmkl))
  for i in range(0,len(benchedmkl)):
    lines = list()
    file_names = list()
    tmp = benchedmkl[i].replace('test','')
    bench_file = 'mkl/'+benchedmkl[i]+'/bench'+tmp
    file_names.append(bench_file)
    len(file_names)

    file_name = file_names[len(file_names)-1]
    # read lines of the benchmark files
    print(file_name)
    f = open(file_name)
    lines.append(f.readlines())
    f.close()

    if int(args.matrixsize) != 1:
      for l in lines[0]:
        if l.find('avg_real_calu_time:') != -1:
          ltmp = l.split(',')
          time_series[len(time_series)-1].append(\
              ltmp[0].replace('avg_real_calu_time:','').strip())
          gflops_series[len(gflops_series)-1].append(\
              float(ltmp[1].replace('avg_Gflops:','').replace('/s','').replace('inf','-1').strip()))
    else:
      ctr = 0
      for l in lines[0]:
        if l.find('avg_real_calu_time:') != -1:
          print(str(ctr)+' -- '+str(threadidx))
          if ctr == threadidx:
            ltmp = l.split(',')
            time_series[len(time_series)-1].append(\
                ltmp[0].replace('avg_real_calu_time:','').strip())
            gflops_series[len(gflops_series)-1].append(\
                float(ltmp[1].replace('avg_Gflops:','').replace('/s','').replace('inf','-1').strip()))
          ctr = ctr + 1

  print(time_series)
  #plot this data

  #line style, sequential method only if start_threads == 1
  stride = 1
  coloring =\
  [\
  '#0099cc','#33cc00','#ff1b54','#0033cc','#9900cc','#800020',\
  '#ff4011','#ffbf01','#00144f','#ff1450',\
  '#0099cc','#33cc00','#cc0033','#0033cc','#9900cc','#800020',\
  '#ff4011','#ffbf01','#00144f','#ff1450',\
  '#0099cc','#33cc00','#cc0033','#0033cc','r','#800020',\
  '#ff4011','#ffbf01','#00144f','#ff1450',\
  '#0099cc','#33cc00','#cc0033','#0033cc','#9900cc','#800020',\
  '#ff4011','#ffbf01','#00144f','#ff1450'\
  ]
  styles = [\
  '-','-','-','-','-','-','-','-','-','-',\
  '--','--','--','--','--','--','--','--','--','--',\
  ':',':',':',':','-',':',':',':',':',':',\
  '-','-','-','-','-','-','-','-','-','-'\
  ]
  markers = [\
  'None','None','None','None','None','None','None','None','None','None',\
  'None','None','None','None','None','None','None','None','None','None',\
  'None','None','None','None','o','None','None','None','None','None',\
  'o','o','o','o','o','o','o','o','o','o'\
  ]
  
  if int(args.matrixsize) != 1:
    pdfname = 'results-calu-mkl-inc-threads-'+str(args.matrixsize)+'-'+str(args.matrixsize)+'.pdf'
  else:
    pdfname = 'results-calu-mkl-inc-matrices-'+str(args.threads)+'.pdf'
  pp =\
  PdfPages(pdfname)
  pl.rc('legend',**{'fontsize':5})
  fig = pl.figure()
  ax = fig.add_subplot(111)
  fig.suptitle('Timings: CALU fully-dynamic scheduling w/ MKL', fontsize=10)
  subtitle = "Computations done on 4 x 8 Intel Xeon E5-4620 @ 2.20GHz NUMA with 4 x 96 GB RAM" 
  if int(args.matrixsize) != 1:
    pl.title('Matrix dimensions: '+dimensions[0]+
    ' x '+dimensions[1]+' (B ~ Blocksize, L ~ Layout)\n'+subtitle, fontsize=8)
  else:
    pl.title('Number of threads: '+str(args.threads)+' (B ~ Blocksize, L ~Layout)\n'+subtitle, fontsize=8)
  if int(args.matrixsize) != 1:
    ax.set_xlabel('Number of threads', fontsize=7)
  else:
    ax.set_xlabel('Size of rows/cols', fontsize=7)

  ax.set_ylabel('Real time in seconds', fontsize=8)

  pl.grid(b=True, which='major', color='k', linewidth=0.3)
  pl.grid(b=True, which='minor', color='k', linewidth=0.1, alpha=0.5)

  ax = pl.gca() 

  group_labels = plot_data

  #ax.set_xticklabels(group_labels)
  data_tmp = range(0,len(plot_data))
  # get right scale for a4 paper size
  scale_tmp = 64 // (len(plot_data)) 
  data = range(0,64,scale_tmp)
  tick_lbs = plot_data
  ax.xaxis.set_ticks(data)
  ax.xaxis.set_ticklabels(tick_lbs)

  p = [None]*len(methodsReal)
  for i in range(0,len(methodsReal)):
    p[i], = ax.plot(data[0:len(time_series[i])], time_series[i], c=coloring[i],
        ls=styles[i], marker=markers[i], markersize=5, label=i, markevery=stride)
  # set 0 as min value for y and 1 as min value for x (data)
  #pl.xlim(xmin=1)
  pl.ylim(ymin=0) 
  
  if int(args.matrixsize) != 1:
    ax.legend((methodsReal),'upper right', shadow=True, fancybox=True)
  else:
    ax.legend((methodsReal),'upper left', shadow=True, fancybox=True)

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
  if int(args.matrixsize) != 1:
    pl.title('Matrix dimensions: '+dimensions[0]+
    ' x '+dimensions[1]+' (B ~ Blocksize, L ~ Layout)\n'+subtitle, fontsize=8)
  else:
    pl.title('Number of threads: '+str(args.threads)+' (B ~ Blocksize, L ~Layout)\n'+subtitle, fontsize=8)
  if int(args.matrixsize) != 1:
    ax.set_xlabel('Number of threads', fontsize=7)
  else:
    ax.set_xlabel('Size of rows/cols', fontsize=7)
  ax.set_ylabel('GFLOPS per second', fontsize=8)

  pl.grid(b=True, which='major', color='k', linewidth=0.3)
  pl.grid(b=True, which='minor', color='k', linewidth=0.1, alpha=0.5)

  ax = pl.gca() 

  #ax.set_xticklabels(group_labels)
  data_tmp = range(0,len(plot_data))
  # get right scale for a4 paper size
  scale_tmp = 64 // (len(plot_data)) 
  data = range(0,64,scale_tmp)
  tick_lbs = plot_data
  ax.xaxis.set_ticks(data)
  ax.xaxis.set_ticklabels(tick_lbs)

  p = [None]*len(methodsReal)
  for i in range(0,len(methodsReal)):
    p[i], = ax.plot(data[0:len(gflops_series[i])], gflops_series[i], c=coloring[i],
        ls=styles[i], marker=markers[i], markersize=5, label=i)
  # set 0 as min value for y and 1 as min value for x (data)
  #pl.xlim(xmin=1)
  pl.ylim(ymin=0)

  # we do not print the legend here, use the one from the timings page
  if int(args.matrixsize) != 1:
    ax.legend((methodsReal),'upper left', shadow=True, fancybox=True)
  else:
    ax.legend((methodsReal),'lower right', shadow=True, fancybox=True)

  ax.legend().set_visible(False)
  # take gflops of best computation to figure out the 
  # granularity of the yaxis
  tmp_ticks = ax.yaxis.get_majorticklocs()
  # note that here "abs()" is needed since if computations are too fast we
  # set GFLOPS to -1 instead of infinity. Since the MultipleLocator must
  # be set to a positive integer value, we have to take care of this case.
  granu = abs(tmp_ticks[len(tmp_ticks)-1]) // (len(tmp_ticks)-1) // 5
  if granu == 0.0:
    granu = 1.0
  print(granu)
  ax.yaxis.set_minor_locator(MultipleLocator(granu))

  pl.tick_params(axis='both', which='major', labelsize=6)
  pl.tick_params(axis='both', which='minor', labelsize=6)

  #pl.savefig('gflops.pdf',format='pdf',papertype='a4',orientation='landscape')
  pl.savefig(pp,format='pdf',papertype='a4',orientation='landscape')
  pp.close()
