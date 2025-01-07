#!/bin/bash -l
#SBATCH --job-name=qe   # Job name
#SBATCH --partition=standard    # partition name
#SBATCH --nodes=2               # Total number of nodes 
#SBATCH --ntasks-per-node=64    # Number of mpi tasks per node
#SBATCH --cpus-per-task=2       # Number of cores (threads) per task
#SBATCH --time=2:30:00       # Run time (d-hh:mm:ss)
#SBATCH --hint=nomultithread
#SBATCH --account=project_465000105 # Project for billing

export MPICH_MAX_THREAD_SAFETY=multiple


# All commands must follow the #SBATCH directives

# Set the number of threads based on --cpus-per-task
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Launch MPI code 
#srun /users/kozhevni/q-e/build/bin/pw.x -i pw.in -npool 112
#srun /users/kozhevni/q-e/build/bin/pw.x -i pw.in -npool 112
srun pw.x -i pw.in -npool 16
