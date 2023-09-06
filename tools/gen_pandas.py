# coding: utf-8

# Very simple script to automatically parse QE results.
# It's not complete, it's not optimized, it's not nice...help it! :)

import glob
import os
import re
import pylab as plt
import pandas as pd

MAX_CPU_LOG_SIZE = 3000    # cpu info are reported in jobscripts or in 
                           # files like "nodes_info". These files are small
                           # so it's better to avoid searching all files for 
                           # these information.

all_data = []


PW_prog_info_re = re.compile("Program (\w+) v.([0-9]*[.][0-9]+) \(svn rev. *([0-9]+)\) starts")
PW_prog_info_alt_re = re.compile("Program (\w+) v.([0-9]*[.][0-9]+)(\w*) *starts")
SIRIUS_prog_info_re = re.compile(" *(SIRIUS) +([0-9]*[.][0-9]+), git hash: (\w+)")
PW_proc_re = re.compile("running on *([0-9]+) *processors",)
PW_proc_re2 = re.compile("Number of MPI processes: *([0-9]+)",)
PW_omp_re = re.compile("Threads/MPI process: +([0-9]+)")
PW_bgrp_re = re.compile("R & G space division: *proc\/nbgrp\/npool\/nimage *= *([0-9]+)")
PW_pool_re = re.compile("K-points division: *npool *= *([0-9]+)")
PW_diag_re = re.compile("a serial algorithm will be used")
PW_diag_re2 = re.compile("size of sub-group: *([0-9]+)\* * ([0-9]+) *procs")
PW_num_el   = re.compile("number of electrons *= *([0-9]*[.][0-9]+)")
PW_num_k   = re.compile("number of k points= *([0-9]+)")
PW_num_KS   = re.compile("number of Kohn-Sham states= *([0-9]+)")
PW_timers_re = re.compile(" *(\w+) *: *([+-]?[0-9]*[.][0-9]+)s CPU *([+-]?[0-9]*[.][0-9]+)s +WALL +\( +[0-9]+ calls\) *")

def collect_data(path, model, lines, valid_k=0, valid_ks=0, valid_e=0):
    global all_data
    timers = {}
    print(path)
    # parse initial part of the file
    line = ''.join(lines[0:800])

    progre=PW_prog_info_re.findall(line)
    if progre:
        app_name, app_ver, app_rev=progre[0]
        
    progre=PW_prog_info_alt_re.findall(line)
    if progre:
        if len(progre[0]) == 2:
            app_name, app_ver, app_rev=progre[0]+('N.A.',)
        elif len(progre[0]) == 3:
            app_name, app_ver, app_rev=progre[0]
        else:
            print("Invalid string version!")

    progre=SIRIUS_prog_info_re.findall(line)
    if progre:
        app_name, app_ver, app_rev=progre[0]
    

        
    nprocre = PW_proc_re.findall(line)
    if nprocre:
        NMPI = int(nprocre[0])
    else:
        nprocre = PW_proc_re2.findall(line)
        if nprocre:
            NMPI = int(nprocre[0])
        else:
            print("FAILED TO PARSE MPI")
            return
    
    ompre = PW_omp_re.findall(line)
    nOMP = 1
    if ompre:
        nOMP = int(ompre[0])
    bgrpre = PW_bgrp_re.findall(line)
    if bgrpre:
        nBGRP = int(bgrpre[0])
        nPOOL = int(NMPI/nBGRP)
    else:
        poolre = PW_pool_re.findall(line)
        if poolre:
            nPOOL = int(poolre[0])
            nBGRP = int(NMPI/nPOOL)
        else:
            print("Failed parsing parallel data")
    diagre = PW_diag_re.findall(line)
    if diagre:
        nDIAG = 1
    diagre = PW_diag_re2.findall(line)
    if diagre:
        nDIAG = int(diagre[0][0])*int(diagre[0][1])
    
    
    # check number of electrons
    el_re = PW_num_el.findall(line)
    if el_re:
        if valid_e == 0:
            electrons = float(el_re[0])
            valid_e = int(electrons)
        else:
            #check match with other output
            electrons = float(el_re[0])
            if abs(int(electrons)-valid_e) > 0:
                print("Unmatched output files...electrons differ")
    
    # check number of k points
    k_re = re.findall("number of k points= *([0-9]+)", line)
    if k_re:
        if valid_k == 0:
            kpoints = int(k_re[0])
            valid_k = kpoints
        else:
            #check match with other output
            kpoints = int(k_re[0])
            if kpoints-valid_k != 0:
                print("Unmatched output files...k points differ")
    
    ks_re = PW_num_KS.findall(line)
    if ks_re:
        if valid_ks == 0:
            nks = int(ks_re[0])
            valid_ks = nks
        else:
            #check match with other output
            nks = int(ks_re[0])
            if nks-valid_ks != 0:
                print("Unmatched output files...k points differ")                
        
    # now parse timers at the end of the file
    line = ''.join(lines[-600:])
    time = PW_timers_re.findall(line)
    if time:
        for t in time:
            timers[t[0]+'_CPU'] = float(t[1])
            timers[t[0]+'_WALL'] = float(t[2])
    
    #try sirius timing like: 
    # qe|ROUTINE_NAME                                                      :      1  1913.1580  1913.1580  1913.1580  1913.1580       0.00
    if app_name == 'SIRIUS':
        time = re.findall("qe\|electrons +: +([0-9]+ +[+-]?[0-9]*[.][0-9]+ +[+-]?[0-9]*[.][0-9]+ +[+-]?[0-9]*[.][0-9]+ +[+-]?[0-9]*[.][0-9]+ +[+-]?[0-9]*[.][0-9]+)", line)
        if time:
            timers['SIRIUS|electrons'] = float(time[0].split()[1])
    
    info = {}
    a,bb = os.path.split(path)
    info['System'] = bb.strip()
    info['InputName'] , info['HPCCenter'] = os.path.split(a)
    info['CPU'] = model
    
    info.update({'AppName':app_name, 'Version':app_ver, 'Revision':app_rev, 'NNodes': 0, \
             'NCores':NMPI*nOMP, 'NMpi': NMPI, 'NOmp': nOMP, 'NPool':nPOOL, 'NBgrp':nBGRP,'NDiag':nDIAG,'Nk': kpoints, 'Nelectrons': electrons, 'Nksstates': nks})
    
    info.update(timers)
    all_data.append(info)
    
    return (valid_k, valid_ks, valid_e)

# this is going to be buggy!!
def is_qe(line):
    if re.findall("Program PWSCF", line):
        return True
    return False

def get_info(path, model):

    valid_k=0; valid_ks=0; valid_e=0
    
    for fname in glob.glob(os.path.join(path,'*')):
        
        # skip directories
        if not os.path.isfile(fname):
            continue
        
        # skip directories    
        with open(fname,'r',encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            n_lines = len(lines)
            
            if not is_qe(''.join(lines[0:min(n_lines,10)])):
                continue
                
            valid_k, valid_ks, valid_e = collect_data(path, model, lines, valid_k, valid_ks, valid_e)
    
    

def save_to_pandas():
    """
    Print the results as a markdown table.
    """
    list_of_keys = set()
    for e in all_data:
        for k in e.keys():
            list_of_keys.add(k)
    
    list_of_keys = list(list_of_keys)
    list_of_types = [None,]*len(list_of_keys)
    
    pd_data = {}
    for i, k in enumerate(list_of_keys):
        pd_data[k] = []
        if not list_of_types[i]:
            for v in all_data:
                if k in v.keys():
                    list_of_types[i] = type(v[k])

    
    for entry in all_data:
        for i, k in enumerate(list_of_keys):
            if k in entry.keys():
                pd_data[k].append(entry[k])
            else:
                if list_of_types[i] == int:
                    pd_data[k].append(-1)
                elif list_of_types[i] == float:
                    pd_data[k].append(-1.0)
                elif list_of_types[i] == str:
                    pd_data[k].append('N.A.')
                else:
                    print("Error, type not implemented")
    df = pd.DataFrame.from_dict(pd_data)
    df.to_pickle("info.pkl")
    
    


def search_for_files():
    """
    Collect and print results
    """
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
                get_info(where, model)
    
if __name__ == "__main__":
    search_for_files()
    save_to_pandas()
