#!/bin/sh
#SBATCH -A c29
#SBATCH -C gpu 
#SBATCH --nodes 3 
##############SBATCH --ntasks 120
#SBATCH --cpus-per-task 1 
#SBATCH --ntasks-per-node 12
#SBATCH -t 4:00:00

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK}
module load daint-gpu
srun -u -n  36 /users/gcistaro/envs/QE_CPU/.spack-env/view/bin/pw2wannier90.x < pw2wann.in > pw2wann.out
