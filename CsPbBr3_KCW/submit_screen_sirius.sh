#!/bin/sh
#SBATCH -A c29
#SBATCH -C gpu 
#SBATCH --nodes 8 
#SBATCH --cpus-per-task 12 
#SBATCH --ntasks-per-node 1
#SBATCH -t 24:00:00

###questo perche dentro kcw tutto e' mpi
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK}
module load daint-gpu

export CRAY_CUDA_MPS=1
export SIRIUS_PRINT_TIMING=1
srun -u -n 8  /users/gcistaro/envs/SIRIUS_GPU/.spack-env/view/bin/kcw.x  -npool 8 < CsPbBr3.screen.in > CsPbBr3.screen.out

