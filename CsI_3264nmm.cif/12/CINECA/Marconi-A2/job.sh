#!/bin/bash
#PBS -N mypw 
#PBS -l select=10:ncpus=64:mpiprocs=64:mem=90GB 
#PBS -l walltime=00:29:59

# Execute QE on 1 to 10 nodes of Intel Xeon Phi 7250.
# The input jobscript can be easily reconstructed from 
#   output file names.
#
# Each node contains 68 cores (with 4 threads per core)
#
#Architecture:          x86_64
#CPU op-mode(s):        32-bit, 64-bit
#Byte Order:            Little Endian
#CPU(s):                272
#On-line CPU(s) list:   0-271
#Thread(s) per core:    4
#Core(s) per socket:    68
#Socket(s):             1
#NUMA node(s):          1
#Vendor ID:             GenuineIntel
#CPU family:            6
#Model:                 87
#Model name:            Intel(R) Xeon Phi(TM) CPU 7250 @ 1.40GHz
#Stepping:              1
#CPU MHz:               1303.640
#BogoMIPS:              2793.49
#L1d cache:             32K
#L1i cache:             32K
#L2 cache:              1024K
#NUMA node0 CPU(s):     0-271



module load autoload intelmpi mkl

cd $PBS_O_WORKDIR
ncpu=`cat $PBS_NODEFILE | wc -w`
nnodes=`cat $PBS_NODEFILE | uniq | wc -w`

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export I_MPI_HYDRA_PMI_CONNECT=alltoall
export KMP_AFFINITY=scatter
export I_MPI_EAGER_THRESHOLD=2097152
export I_MPI_INTRANODE_EAGER_THRESHOLD=2097152
export KMP_AFFINITY=scatter,granularity=fine,1

INPUT=pw.in

NPOOL=48
NTG=1
NDIAG=16

# pure MPI pw.x
mpirun ./pw.x -inp $INPUT -npool $NPOOL -ndiag $NDIAG -ntg $NTG > ${nnodes}n_${ncpu}c_${OMP_NUM_THREADS}o_${NPOOL}p_${NTG}tg_${NDIAG}ndiag.out 

