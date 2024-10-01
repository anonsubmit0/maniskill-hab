#!/usr/bin/bash

# shellcheck disable=SC2045

for task in $(ls -1 "mshab_checkpoints/rl")
do
    for subtask in $(ls -1 "mshab_checkpoints/$task")
    do
        for obj_name in $(ls -1 "mshab_checkpoints/rl/$task/$subtask")
        do
            if [[ ! -e "mshab_exps/gen_data_save_trajectories/$task/$subtask/train/$obj_name" && $obj_name != "all" ]]; then
                python gen_data.py "$task" "$subtask" "$obj_name"
            fi
        done
    done
done