#!/bin/bash
#PBS -N mpipw
#PBS -A cin_staff 
#PBS -l select=1:ncpus=64:mpiprocs=64:mem=90GB 
#PBS -l walltime=01:29:59

# version is  2017.0 Update 1 Product build 20161005
module load autoload intelmpi mkl

cd $PBS_O_WORKDIR
#cat $PBS_NODEFILE
ncpu=`cat $PBS_NODEFILE | wc -w`
nnodes=`cat $PBS_NODEFILE | uniq | wc -w`

lscpu > node_info

export I_MPI_HYDRA_PMI_CONNECT=alltoall
export I_MPI_EAGER_THRESHOLD=2097152
export I_MPI_INTRANODE_EAGER_THRESHOLD=2097152
export KMP_AFFINITY=scatter,granularity=fine,1

# MPI only pw.x
EXEC=./pw.x
INPUT=./pw.in
NPOOL=128
NTG=1
NDIAG=1

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
mpirun $EXEC -inp $INPUT -npool $NPOOL -ndiag $NDIAG -ntg $NTG > pw-${nnodes}n_${ncpu}c_${OMP_NUM_THREADS}o_${NPOOL}p_${NTG}tg_${NDIAG}diag.out 

