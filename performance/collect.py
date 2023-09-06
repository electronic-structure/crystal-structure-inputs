import os
import shutil
import subprocess
import argparse
import re
import sys
import json

parser = argparse.ArgumentParser(description='Make a timing plot.')
parser.add_argument('DIR', help='Root directory with the location of the benchmark.')
args = parser.parse_args()

def get_qe_time(fname):
    f = open(fname, 'r')
    result = 0
    for line in f.readlines():
        # PWSCF        :  27m49.03s CPU  11m50.52s WALL
        m = re.search('\s+PWSCF\s+:(.*)CPU(.*)WALL', line)
        # match is successful
        if m:
            val = 0
            # try to match 'XmY.YYs'
            m1 = re.search('(\d+)m\s*(\d+)\.(\d+)s', m.group(2).strip())
            if m1:
                val = 60 * int(m1.group(1)) + int(m1.group(2))
            else:
                # try to match XhYm
                m1 = re.search('(\d+)h\s*(\d+)m', m.group(2).strip())
                if m1:
                    val = 3600 * int(m1.group(1)) + 60 * int(m1.group(2))

            print("%s  ---> %i sec."%(m.group(0), val))
            result = val

    f.close()
    return result

def get_qe_energy(fname):
    f = open(fname, 'r').read()
    m = re.search('Username.*\n.*\n\s*(\w*)\s*(\w*)\s*(\w*)\s*(\w*)\s*([0-9]*\.[0-9]*)\skJ', f)
    if m:
        return float(m.group(5))
    else:
        return 0

def main():

    title = os.path.basename(args.DIR)

    print(f"Looking in {args.DIR}")

    results = {}
    results["data"] = {}

    for root, label, files in os.walk(args.DIR):
        for f in files:
            if f == 'slurm-stdout.txt':
                p, task_id = os.path.split(root)
                p, label = os.path.split(p)
                m = re.search('(\d+)N_(\d+)R_(\d+)T', task_id)
                N = int(m.group(1))
                print(f"nodes: {N}, task layout: {task_id}")
                if label not in results["data"]:
                    results["data"][label] = []
                scf_time = get_qe_time(f"{root}/slurm-stdout.txt")
                energy = get_qe_energy(f"{root}/slurm-stdout.txt")
                r = {'nodes' : N, 'scf_time' : scf_time, 'energy' : energy,
                     'ranks' : int(m.group(2)), 'threads_per_rank' : int(m.group(3))}
                results["data"][label].append(r)

    results['title'] = title
    results['energy_units'] = 'kJ'
    results['time_units'] = 's'
    with open(f"{title}.json", "w") as out:
        out.write(json.dumps(results,  indent=4))

    return


if __name__ == "__main__":
    main()
