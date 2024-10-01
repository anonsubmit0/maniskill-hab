#!/usr/bin/bash

# mv old results in case already there
bench_types=("simple_bench" "realistic_bench" "interact_bench")
for btype in "${bench_types[@]}"
do
    i=0
    while true; do
        new_file="bench/results/${btype}_${i}.json"
        if [ ! -e "$new_file" ]; then
            mv "bench/results/$btype.json" "$new_file"
            echo "bench/results/$btype.json copied to $new_file"
            break
        fi
        ((i++))
    done
done

HAB_NUM_ENVS=(1 2 4 8 16 32 48)

MS3_NUM_ENVS=(64 128 256 512 1024)

NUM_RUNS=10

for seed in $(seq 1 $NUM_RUNS)
do 
    for num_envs in "${HAB_NUM_ENVS[@]}"
    do
        echo "HAB: HabitatInteractNoConcur SEED $seed NUM_ENVS $num_envs interact"
        python -m bench.bench --seed "$seed" --num-envs "$num_envs" --bench-preset HabitatInteractNoConcur --bench-type "interact"
    done

    for num_envs in "${MS3_NUM_ENVS[@]}"
    do
        echo "MS3: MSInteract SEED $seed NUM_ENVS $num_envs interact"
        python -m bench.bench --seed "$seed" --num-envs "$num_envs" --bench-preset MSInteract --bench-type "interact"
    done
done
