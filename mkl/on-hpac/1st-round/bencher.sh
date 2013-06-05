#! /bin/sh

export LD_LIBRARY_PATH=/home/eder/intel/composerxe/mkl/lib/intel64:$LD_LIBRARY_PATH
./bench-mkl.py -a1 -c8 -s1 -b2 -t64 -m8192 -n8192 -p 
./bench-mkl.py -a1 -c8 -s1 -b2 -t64 -m16384 -n16384 -p 
./bench-mkl.py -a1 -c8 -s1 -b2 -t64 -m32768 -n32768 -p 
