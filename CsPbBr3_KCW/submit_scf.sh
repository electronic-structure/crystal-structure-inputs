#!/bin/sh
#SBATCH -A c29
#SBATCH -C gpu 
#SBATCH --nodes 10 
##############SBATCH --ntasks 120
#SBATCH --cpus-per-task 1 
#SBATCH --ntasks-per-node 12
	#SBATCH -t 5:00:00

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK}
module load daint-gpu
srun -u -n  120 /users/gcistaro/envs/QE_CPU/.spack-env/view/bin/pw.x -npool 10 < pbe50.scf.in > pbe50.scf.out
