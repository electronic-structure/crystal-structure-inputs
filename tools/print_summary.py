# coding: utf-8

# Very simple script to automatically generate a short summary of the results.
# It's not complete, it's not optimized, it's not nice...help it! :)

import glob
import os
import re

REPORTED_TIMER="electrons"
MAX_CPU_LOG_SIZE = 3000    # cpu info are reported in jobscripts or in 
                           # files like "nodes_info". These files are small
                           # so it's better to avoid searching all files for 
                           # these information.
                           
header="""
| Input                                                        | CPU                                                          | electrons | k-points  | Best time |
| ------------------------------------------------------------ | ------------------------------------------------------------ | --------- | --------- | --------- |"""


def get_info(path, routine):
    best_time = 1e10
    electrons = -1.0
    kpoints = -1
    for fname in glob.glob(os.path.join(path,'*')):
        got_k = False
        got_e = False
        
        # skip directories
        if not os.path.isfile(fname):
            continue
        
        # skip directories    
        with open(fname,'r',encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            n_lines = len(lines)
            for i, l in enumerate(lines):
                # check number of electrons
                el_re=[]
                if not got_e:
                    el_re = re.findall("number of electrons *= *([0-9]*[.][0-9]+)", l)
                if el_re:
                    got_e = True
                    if electrons == -1:
                        electrons = float(el_re[0])
                    else:
                        #check match with other output
                        e = float(el_re[0])
                        if abs(e-electrons) > 1e-6:
                            print("Unmatched output files...electrons differ")
                
                # check number of k points
                k_re=[]
                if not got_k:
                    k_re = re.findall("number of k points= *([0-9]+)", l)
                if k_re:
                    got_k = True
                    if kpoints == -1:
                        kpoints = int(k_re[0])
                    else:
                        #check match with other output
                        k = int(k_re[0])
                        if k-kpoints > 0:
                            print("Unmatched output files...k points differ")
                
                # get timers, but just for last lines (otherwise is too slow!)
                if i < (n_lines-100):
                    continue
                time = re.findall(routine+" *: *([+-]?[0-9]*[.][0-9]+)s CPU *([+-]?[0-9]*[.][0-9]+)s", l)
                if time:
                    if float(time[0][1]) < best_time:
                        best_time = float(time[0][1])
                    # time is the last thing we need so break now
                    break
    return [electrons, kpoints, best_time]

def add_to_table(w,m,e, k, b):
    """
    Print the results as a markdown table.
    """
    print ("| {:60s} | {:60s} | {:9.2f} | {:9d} | {:9.2f} |".format(w,m,e,k,b))

def print_summary():
    """
    Collect and print results
    """
    print(header)
    for fname in glob.glob('**',recursive=True):
        # skip directories
        if os.path.isdir(fname):
            continue
        # large files are pseudopotentials or PW outputs... but this limit may be low
        if (os.path.getsize(fname) > MAX_CPU_LOG_SIZE):
            continue
        with open(fname,'r',encoding='utf-8', errors='ignore') as f:
            # check cpu model with re...
            model =  re.findall("odel name\s*\t*:(.*)", f.read())
            # now go get timers!
            if model:
                model = model[0].strip()
                where = os.path.split(fname)[0].strip()
                electrons, kpoints, bestt = get_info(where, REPORTED_TIMER)
                add_to_table(where, model, electrons, kpoints, bestt)
    
if __name__ == "__main__":
    print_summary()
