#! /bin/sh

export LD_LIBRARY_PATH=/home/eder/intel/composerxe/mkl/lib/intel64:$LD_LIBRARY_PATH
./bench-mkl.py -a1 -c8 -s4 -b2 -t64 -m8000 -n8000 -p 
./bench-mkl.py -a1 -c8 -s4 -b2 -t64 -m12000 -n12000 -p 
./bench-mkl.py -a1 -c8 -s4 -b2 -t64 -m16000 -n16000 -p 
./bench-mkl.py -a1 -c8 -s4 -b2 -t64 -m20000 -n20000 -p 
./bench-mkl.py -a1 -c8 -s4 -b2 -t64 -m24000 -n24000 -p 
./bench-mkl.py -a1 -c8 -s4 -b2 -t64 -m28000 -n28000 -p 
./bench-mkl.py -a1 -c8 -s4 -b2 -t64 -m32000 -n32000 -p 
./bench-mkl.py -a1 -c8 -s4 -b2 -t64 -m36000 -n36000 -p 
./bench-mkl.py -a1 -c8 -s4 -b2 -t64 -m40000 -n40000 -p 
./bench-mkl.py -a1 -c8 -s4 -b2 -t64 -m44000 -n44000 -p 
./bench-mkl.py -a1 -c8 -s4 -b2 -t64 -m48000 -n48000 -p 
