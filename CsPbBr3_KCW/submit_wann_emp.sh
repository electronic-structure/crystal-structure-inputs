#!/bin/sh
#SBATCH -A c29
#SBATCH -C gpu 
#SBATCH --nodes 1 
##############SBATCH --ntasks 120
#SBATCH --cpus-per-task 1 
#SBATCH --ntasks-per-node 1
#SBATCH -t 24:00:00

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK}
module load daint-gpu
srun -u -n  1 /users/gcistaro/envs/QE_CPU/.spack-env/view/bin/wannier90.x CsPbBr3_emp
