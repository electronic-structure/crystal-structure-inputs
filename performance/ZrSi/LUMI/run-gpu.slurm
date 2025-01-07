#!/bin/bash -l
#SBATCH --job-name=test   # Job name
#SBATCH --partition=standard-g  # partition name
#SBATCH --nodes=7               # Total number of nodes 
#SBATCH --ntasks-per-node=8     # 8 MPI ranks per node, 16 total (2x8)
#SBATCH --gpus-per-node=8       # Allocate one gpu per MPI rank
#SBATCH --time=0:40:00          # Run time (d-hh:mm:ss)
#SBATCH --account=project_465000105 # Project for billing

cat << EOF > select_gpu
#!/bin/bash

export ROCR_VISIBLE_DEVICES=\$SLURM_LOCALID
exec \$*
EOF

chmod +x ./select_gpu

CPU_BIND="mask_cpu:7e000000000000,7e00000000000000"
CPU_BIND="${CPU_BIND},7e0000,7e000000"
CPU_BIND="${CPU_BIND},7e,7e00"
CPU_BIND="${CPU_BIND},7e00000000,7e0000000000"

export OMP_NUM_THREADS=6

export SIRIUS_VERBOSITY=2
export SIRIUS_EV_SOLVER=dlaf
export SIRIUS_PRINT_TIMING=3
export SIRIUS_CONFIG=cfg.json

srun --cpu-bind=${CPU_BIND} ./select_gpu /pfs/lustrep4/users/kozhevni/spack-env/qe-sirius/.spack-env/view/bin/pw.x -i pw.in -npool 56
rm -rf ./select_gpu
