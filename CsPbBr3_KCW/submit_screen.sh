#!/bin/sh
#SBATCH -A c29
#SBATCH -C gpu 
#SBATCH --nodes 8 
##############SBATCH --ntasks 120
#SBATCH --cpus-per-task 1
#SBATCH --ntasks-per-node 12 
#SBATCH -t 18:00:00

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK}
module load daint-gpu
srun -u -n 96 /users/gcistaro/envs/QE_CPU/.spack-env/view/bin/kcw.x -npool 8 < CsPbBr3.screen.in > CsPbBr3.screen.out
