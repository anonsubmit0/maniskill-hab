#!/usr/bin/bash

SEED=0

trajs_per_obj=1000
epochs=10

TASK=tidy_house
SUBTASK=pick
SPLIT=train
OBJ=all

# shellcheck disable=SC2001
ENV_ID="$(echo $SUBTASK | sed 's/\b\(.\)/\u\1/g')SubtaskTrain-v0"
WORKSPACE="mshab_exps"
GROUP=$TASK-rcad-bc-$SUBTASK
EXP_NAME="$ENV_ID/$GROUP/bc-$SUBTASK-$OBJ-local-trajs_per_obj=$trajs_per_obj"
# shellcheck disable=SC2001
PROJECT_NAME="MS-HAB-RCAD-bc"

WANDB=True
TENSORBOARD=True
MS_ASSET_DIR="$HOME/.maniskill/data"

resume_logdir="$WORKSPACE/$EXP_NAME"
resume_config="$resume_logdir/config.yml"

max_cache_size=300000   # safe num for about 64 GiB system memory

if [[ $SUBTASK == "open" || $SUBTASK == "close" ]]; then
    data_dir_fp="$MS_ASSET_DIR/scene_datasets/replica_cad_dataset/rearrange-dataset/$TASK/$SUBTASK/$OBJ.h5"
else
    data_dir_fp="$MS_ASSET_DIR/scene_datasets/replica_cad_dataset/rearrange-dataset/$TASK/$SUBTASK"
fi

attempt=0

# while true
# do

echo "RUNNING $attempt"

if [ -f "$resume_config" ] && [ -f "$resume_logdir/models/latest.pt" ]; then
    echo "RESUMING $attempt"
    SAPIEN_NO_DISPLAY=1 python train_bc.py "$resume_config" resume_logdir="$resume_logdir" \
        logger.clear_out="False" \
        logger.wandb_cfg.group="$GROUP" \
        logger.exp_name="$EXP_NAME" \
        seed=$SEED \
        eval_env.env_id="$ENV_ID" \
        eval_env.task_plan_fp="task_plans/$TASK/$SUBTASK/$SPLIT/$OBJ.json" \
        eval_env.spawn_data_fp="$MS_ASSET_DIR/scene_datasets/replica_cad_dataset/rearrange/spawn_data/$TASK/$SUBTASK/$SPLIT/spawn_data.pt" \
        eval_env.frame_stack=1 \
        algo.epochs=$epochs \
        algo.trajs_per_obj=$trajs_per_obj \
        algo.data_dir_fp="$data_dir_fp" \
        algo.max_cache_size=$max_cache_size \
        algo.eval_freq=1 \
        algo.log_freq=1 \
        algo.save_freq=1 \
        eval_env.make_env="True" \
        eval_env.num_envs=252 \
        algo.eval_episodes=252 \
        eval_env.max_episode_steps=200 \
        eval_env.record_video="False" \
        eval_env.info_on_video="False" \
        eval_env.save_video_freq=1 \
        logger.best_stats_cfg="{eval/success_once: 1, eval/return_per_step: 1}" \
        logger.wandb="$WANDB" \
        logger.tensorboard="$TENSORBOARD" \
        logger.project_name="$PROJECT_NAME" \
        logger.workspace="$WORKSPACE" \
        
else
    echo "STARTING $attempt"
    SAPIEN_NO_DISPLAY=1 python train_bc.py configs/bc_pick.yml \
        logger.clear_out="True" \
        logger.wandb_cfg.group="$GROUP" \
        logger.exp_name="$EXP_NAME" \
        seed=$SEED \
        eval_env.env_id="$ENV_ID" \
        eval_env.task_plan_fp="task_plans/$TASK/$SUBTASK/$SPLIT/$OBJ.json" \
        eval_env.spawn_data_fp="$MS_ASSET_DIR/scene_datasets/replica_cad_dataset/rearrange/spawn_data/$TASK/$SUBTASK/$SPLIT/spawn_data.pt" \
        eval_env.frame_stack=1 \
        algo.epochs=$epochs \
        algo.trajs_per_obj=$trajs_per_obj \
        algo.data_dir_fp="$data_dir_fp" \
        algo.max_cache_size=$max_cache_size \
        algo.eval_freq=1 \
        algo.log_freq=1 \
        algo.save_freq=1 \
        eval_env.make_env="True" \
        eval_env.num_envs=252 \
        algo.eval_episodes=252 \
        eval_env.max_episode_steps=200 \
        eval_env.record_video="False" \
        eval_env.info_on_video="False" \
        eval_env.save_video_freq=1 \
        logger.best_stats_cfg="{eval/success_once: 1, eval/return_per_step: 1}" \
        logger.wandb="$WANDB" \
        logger.tensorboard="$TENSORBOARD" \
        logger.project_name="$PROJECT_NAME" \
        logger.workspace="$WORKSPACE" \
        
fi

sleep 300

attempt=$((attempt+1))

# done
