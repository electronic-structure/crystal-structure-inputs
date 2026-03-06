#!/bin/bash

export NODES=1
export TASKSPERNODE=8
export CPUSPERTASK=12

suffix="${NODES}N_${TASKSPERNODE}R_${CPUSPERTASK}T"
json_file="jobs_${suffix}.json"
rm -f "$json_file"
echo '{}' > "$json_file"

for i in {0..9}; do
  key="run${i}"
  label="${key}_${suffix}"
  mkdir -p $label
  # create job submission script from the template
  envsubst '$NODES $TASKSPERNODE $CPUSPERTASK' < run.slrm.template > $label/run.slrm
  # copy input files
  cp Si.json Ge.json sirius.json $label/
  # lauch job
  cd $label
  jobid=$(sbatch run.slrm | awk '{print $4}')
  cd ..
  # add key:value pair
  new_json=$(jq --arg k "$key" --arg id "$jobid" \
      '. + {($k): ($id|tonumber)}' "$json_file")
  printf '%s\n' "$new_json" > "$json_file"
done

