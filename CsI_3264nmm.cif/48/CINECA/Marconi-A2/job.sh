#!/bin/bash
#PBS -N mypw 
#PBS -A cin_staff 
#PBS -l select=8:ncpus=64:mpiprocs=32:mem=90GB 
#PBS -l walltime=16:28:00

# Execute QE MPI+OpenMP & ELPA on 8 and 16 nodes of Intel Xeon Phi 7250.
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

module load env-knl
module load profile/knl
module load autoload qe

cd $PBS_O_WORKDIR
#cat $PBS_NODEFILE
ncpu=`cat $PBS_NODEFILE | wc -w`
nnodes=`cat $PBS_NODEFILE | uniq | wc -w`

export OMP_NUM_THREADS=2
export MKL_NUM_THREADS=2
export I_MPI_HYDRA_PMI_CONNECT=alltoall
export KMP_AFFINITY=scatter
export I_MPI_EAGER_THRESHOLD=2097152
export I_MPI_INTRANODE_EAGER_THRESHOLD=2097152
export KMP_AFFINITY=scatter,granularity=fine,1

INPUT=pw.in
#INPUT=La3Li7O12Zr2_cubic_422259.in
NPOOL=16
NTG=4
NDIAG=16

mpirun pw.x -inp $INPUT -npool $NPOOL -ndiag $NDIAG -ntg $NTG > pw-avx512-cineca/${nnodes}n_${ncpu}c_${OMP_NUM_THREADS}o_${NPOOL}p_${NTG}tg_${NDIAG}diag.out

