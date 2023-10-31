#!/bin/sh
#SBATCH -A c29
#SBATCH -C gpu 
#SBATCH --nodes 16 
##############SBATCH --ntasks 120
#SBATCH --cpus-per-task 1 
#SBATCH --ntasks-per-node 12
#SBATCH -t 24:00:00

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK}
module load daint-gpu
srun -u -n  192 /users/gcistaro/envs/QE_CPU/.spack-env/view/bin/kcw.x -npool 16 < CsPbBr3.wann2kcw.in > CsPbBr3.wann2kcw.out
