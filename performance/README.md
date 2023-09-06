A collection of performance benchmarks for QE

1. To submit jobs, run:
```bash
python job_launch.py Au-surf -i pw.in -p mc -t 3 -c 'pw.x' -k 2 -n 12 24 36 48 -T '0:20:00' -l 'qe_cscs_67' -R
python job_launch.py Au-surf -i pw.in -p gpu -t 12 -c 'pw.x -sirius_scf' -k 2 -n 1 2 3 4 -T '0:20:00' -l 'qe_sirius' -R
 ```

2. To collect data, run:
```bash
python collect.py $SCRATCH/Au-surf
```

3. To produce a plot, run:
```bash
python plot.py -x nodes:Nodes -y scf_time:SCF Au-surf.json "qe_cscs_67:QE-6.7 CPU" "qe_sirius:QE+SIRIUS GPU"
```

# Individual benchmarks

## Si511Ge
```bash
# run on 4, 9, 16 and 25 nodes with 9 threads/rank and 4 ranks/node
python job_launch.py Si511Ge -i pw.in -p mc -t 9 -c 'pw.x' -k 1 -n 16 36 64 100 -T '0:30:00' -l 'qe_cscs_67' -R
```

## Au-surf
```bash
# run on 1, 2, 3, 4, nodes with 12 threads/ranks and 1 rank/node
python job_launch.py Au-surf -i pw.in -p gpu -t 12 -c 'pw.x -sirius_scf' -k 2 -n 1 2 3 4 -T '0:20:00' -l 'qe_sirius' -R
```

## B6Ni8
```bash
# run on 4, 8, 16, 32 nodes with 3 threads/rank and 12 ranks/node
python job_launch.py B6Ni8 -i pw.in -p mc -t 3 -c 'pw.x' -k 48 96 192 384 -n 1 -T '0:30:00' -l 'qe_cscs_67' -R
# run with QE-cuf
python job_launch.py B6Ni8 -i pw.in -p gpu -t 6 -c 'pw.x' -k 8 16 32 64 -n 1 -T '0:30:00' -l 'qe_gpu_cscs_66a2' -R
```

## ZrSi
```bash
python3 job_launch.py ZrSi -i pw.in -p gpu -t 12 -c 'pw.x -sirius_scf' -k 14 28 56 112 -n 1 -T '0:40:00' -l 'qe_sirius' -R
python3 job_launch.py ZrSi -i pw.in -p gpu -t 12 -c 'pw.x' -k 14 28 56 112 -n 1 -T '0:40:00' -l 'qe_66a2_cscs' -RA
python3 collect.py $SCRATCH/ZrSi
```
