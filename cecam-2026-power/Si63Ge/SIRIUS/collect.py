#!/usr/bin/env python3
import json
import re
import sys
import subprocess
from pathlib import Path
from statistics import mean, stdev

RE_KJ = re.compile(r"^\s*sirius\s*:\s*1\s+([0-9]+(?:\.[0-9]+)?)\s*kJ\b", re.MULTILINE)
RE_S  = re.compile(r"^\s*sirius\s+1\s+([0-9]+(?:\.[0-9]+)?)\s*s\b", re.MULTILINE)

def extract_suffix(json_path: Path) -> str:
    m = re.match(r"^jobs_(.+)\.json$", json_path.name)
    if not m:
        raise ValueError(f"Unexpected filename: {json_path.name}")
    return m.group(1)

def safe_stdev(values):
    if len(values) >= 2:
        return stdev(values)
    if len(values) == 1:
        return 0.0
    return None

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} jobs_<suffix>.json")
        sys.exit(2)

    json_path = Path(sys.argv[1]).resolve()
    suffix = extract_suffix(json_path)
    base_dir = json_path.parent

    print(suffix)
    m = re.match(r'(\d+)N_(\d+)R_(\d+)T', suffix)
    nnodes, r, t = m.groups()
    nnodes = int(nnodes)
    print(f"nodes: {nnodes}  ranks/node: {r}  threads/rank: {t}")

    with json_path.open() as f:
        jobs = json.load(f)

    energies = []
    energies_slurm = []
    times = []

    print("run  jobid  energy_kJ  energy_slurm_kJ  time_s")

    for key in sorted(jobs):
        jobid = jobs[key]

        cmd = ["sacct", "-X", "-n", "-P", "-j", str(jobid), "-o", "ConsumedEnergy"]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        m = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)K\s*", result.stdout)
        if not m:
            raise ValueError(f"Unexpected ConsumedEnergy format: {out!r}")
	
        energy_slurm_kj = float(m.group(1))

        run_dir = base_dir / f"{key}_{suffix}"
        out_file = run_dir / f"slurm-{jobid}.out"

        if not out_file.exists():
            print(f"{key}: missing {out_file}", file=sys.stderr)
            continue

        text = out_file.read_text(errors="replace")

        m_kj = RE_KJ.search(text)
        m_s  = RE_S.search(text)

        if not m_kj or not m_s:
            print(f"{key}: pattern not found", file=sys.stderr)
            continue

        energy_kj = float(m_kj.group(1))
        time_s = float(m_s.group(1))

        energies.append(energy_kj)
        energies_slurm.append(energy_slurm_kj)
        times.append(time_s)

        print(f"{key}  {jobid}  {energy_kj}  {energy_slurm_kj}  {time_s}")

    if not energies or not times:
        print("\nNo valid data found.")
        sys.exit(1)

    e_mean = mean(energies)
    e_sd = safe_stdev(energies)

    e_slurm_mean = mean(energies_slurm)
    e_slurm_sd = safe_stdev(energies_slurm)

    t_mean = mean(times)
    t_sd = safe_stdev(times)

    # Power in Watts: (kJ * 1000) / s
    power_w = (e_mean * 1000.0) / t_mean

    energy_kWh = e_mean / 3600
    
    print("Report")
    print(f"energy : total {e_slurm_mean:.2f} ± {e_slurm_sd:.2f} kJ, user {e_mean:.2f} ± {e_sd:.2f} kJ, difference {e_slurm_mean - e_mean:.2f} kJ")
    print(f"time   : {t_mean:.2f} sec.")
    print(f"resource : {nnodes * t_mean / 3600:.4f} node-hours")
    print(f"power  : {power_w:.2f} W")
    print(f"energy : {energy_kWh:.4f} kWh")
    print(f"energy : {energy_kWh * 0.22:.4f} CHF")

if __name__ == "__main__":
    main()
