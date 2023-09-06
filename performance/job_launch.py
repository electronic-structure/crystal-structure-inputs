import os
import shutil
import subprocess
import argparse

num_threads_per_node = {'mc' : 36, 'gpu' : 12}

new_env = os.environ.copy()

parser = argparse.ArgumentParser(description='Launch QE jobs.')
parser.add_argument('DIR', help='Directory with the test')
parser.add_argument('-i', '--input', help='Input file name', default='pw.in')
parser.add_argument('-p', '--partition', help='Target partition', choices=['mc', 'gpu'], default='mc')
parser.add_argument('-t', '--threads', type=int, help='Number of threads per rank', default=6)
parser.add_argument('-s', '--scratch', help='Scratch directory', default=f"{new_env['SCRATCH']}")
parser.add_argument('-c', '--command', help='Execution command', default='pw.x')
parser.add_argument('-k', '--kpool', type=int, nargs='+', help='Number of k-point pools', default=[1])
parser.add_argument('-n', '--ndiag', type=int, nargs='+', help='Number of ranks for band parallelisation', default=[1])
parser.add_argument('-R', '--run', action='store_true', help='Submit the jobs')
parser.add_argument('-T', '--time', help='max. execution time', default='0:30:00')
parser.add_argument('-l', '--label', help='common label for the collection of tests', default='qe')
args = parser.parse_args()

def main():

    # store the test in {SCRATCH}/{DIR}/{LABEL}/{xN_yR_zT}
    target_dir = f"{args.scratch}/{os.path.basename(args.DIR)}/{args.label}"
    print("Terget directory: %s"%target_dir)

    os.makedirs(target_dir, exist_ok=True)

    if num_threads_per_node[args.partition] % args.threads:
        raise RuntimeError(f"wrong number of threads per rank: {args.threads}")

    num_ranks_per_node = int(num_threads_per_node[args.partition] / args.threads)

    for k in args.kpool:
        for nd in args.ndiag:
            num_ranks = k * nd
            if num_ranks % num_ranks_per_node:
                raise RuntimeError(f"number of ranks ({num_ranks}) is not optimal for {num_ranks_per_node} ranks/node")


    for k in args.kpool:

        for nd in args.ndiag:

            num_ranks = k * nd
            num_nodes = int(num_ranks / num_ranks_per_node) + min(1, num_ranks % num_ranks_per_node)
            label = f"{num_nodes}N_{num_ranks}R_{args.threads}T"

            target_subdir = f"{target_dir}/{label}"
            if os.path.exists(target_subdir):
                shutil.rmtree(target_subdir)

            shutil.copytree(args.DIR, f"{target_subdir}/")

            with open(f"{target_subdir}/run.slrm", 'w') as f:
                f.write('#!/bin/bash -l\n')
                f.write('#SBATCH --job-name="test_scf"\n')
                f.write(f'#SBATCH --nodes={num_nodes}\n')
                f.write(f'#SBATCH --time={args.time}\n')
                f.write('#SBATCH --output=slurm-stdout.txt\n')
                f.write('#SBATCH --error=slurm-stderr.txt\n')
                f.write('#SBATCH --account=csstaff\n')
                f.write(f'#SBATCH -C {args.partition}\n')
                f.write(f'export MKL_NUM_THREADS={args.threads}\n')
                f.write(f'export OMP_NUM_THREADS={args.threads}\n')
                if num_ranks_per_node > 1:
                    f.write('export CRAY_CUDA_MPS=1\n')

                cmd = (
                    f"srun -n {num_ranks} --hint=nomultithread --unbuffered -c {args.threads} "
                    f"{args.command} -i {args.input} -npool {k} -ndiag {nd}\n"
                )
                f.write(cmd)

            if (args.run):
                print(f"Sumbinning the job: {label}")
                p = subprocess.Popen(["sbatch", "run.slrm"], cwd = target_subdir)
                p.wait()
    return


if __name__ == "__main__":
    main()
