#!/usr/bin/bash

SEED=0

TASK=tidy_house
SUBTASK=pick
SPLIT=train
OBJ=003_cracker_box

# shellcheck disable=SC2001
ENV_ID="$(echo $SUBTASK | sed 's/\b\(.\)/\u\1/g')SubtaskTrain-v0"
WORKSPACE="mshab_exps"
GROUP=$TASK-rcad-sac-$SUBTASK
EXP_NAME="$ENV_ID/$GROUP/sac-$SUBTASK-$OBJ-local"
# shellcheck disable=SC2001
PROJECT_NAME="MS-HAB-RCAD-$(echo $SUBTASK | sed 's/\b\(.\)/\u\1/g')-$TASK-sac"

WANDB=False
MS_ASSET_DIR="$HOME/.maniskill/data"


SAPIEN_NO_DISPLAY=1 python train_sac.py configs/sac_pick.yml \
        logger.clear_out="True" \
        logger.wandb_cfg.group="$GROUP" \
        logger.exp_name="$EXP_NAME" \
        seed=$SEED \
        env.env_id="$ENV_ID" \
        env.task_plan_fp="task_plans/$TASK/$SUBTASK/$SPLIT/$OBJ.json" \
        env.spawn_data_fp="$MS_ASSET_DIR/scene_datasets/replica_cad_dataset/rearrange/spawn_data/$TASK/$SUBTASK/$SPLIT/spawn_data.pt" \
        \
        algo.gamma=0.9 \
        algo.total_timesteps=50000000 \
        algo.eval_freq=100000 \
        algo.log_freq=10000 \
        algo.save_freq=100000 \
        algo.batch_size=512 \
        algo.replay_buffer_capacity=100000 \
        \
        eval_env.make_env="True" \
        env.make_env="True" \
        \
        env.num_envs=63 \
        eval_env.num_envs=63 \
        \
        algo.eval_episodes=63 \
        \
        env.max_episode_steps=100 \
        eval_env.max_episode_steps=200 \
        \
        env.record_video="False" \
        env.info_on_video="False" \
        \
        eval_env.record_video="True" \
        eval_env.info_on_video="False" \
        eval_env.save_video_freq=10 \
        \
        logger.best_stats_cfg="{eval/success_once: 1, eval/return_per_step: 1}" \
        logger.wandb="$WANDB" \
        logger.tensorboard="False" \
        logger.project_name="$PROJECT_NAME" \
        logger.workspace="$WORKSPACE" \
