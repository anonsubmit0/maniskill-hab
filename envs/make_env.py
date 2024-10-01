from dataclasses import field, dataclass
from pathlib import Path
from typing import Dict, List, Union, Optional

import gymnasium as gym

import mani_skill.envs
from mani_skill.vector.wrappers.gymnasium import ManiSkillVectorEnv

from .wrappers.record import RecordEpisode
from .wrappers.vector import VectorRecordEpisodeStatistics
from .sequential_task import SequentialTaskEnv
from .pick import PickSubtaskTrainEnv
from .place import PlaceSubtaskTrainEnv
from .open import OpenSubtaskTrainEnv
from .close import CloseSubtaskTrainEnv
from .planner import plan_data_from_file
from .wrappers import FetchActionWrapper
from .wrappers.pixel_obs import FetchDepthObservationWrapper, FrameStack
from .wrappers.record_gpu import RecordVideoGPU


def recursive_fix_env_kwargs(env_kwargs, inplace=False):
    if isinstance(env_kwargs, dict):
        if inplace:
            for k, v in env_kwargs.items():
                env_kwargs[k] = recursive_fix_env_kwargs(v)
            return env_kwargs
        return dict((k, recursive_fix_env_kwargs(v)) for k, v in env_kwargs.items())
    if isinstance(env_kwargs, str):
        if env_kwargs == "None":
            return None
        if env_kwargs == "True":
            return True
        if env_kwargs == "False":
            return False
        if "<list>" in env_kwargs and "</list>" in env_kwargs:
            env_kwargs = env_kwargs.replace("<list>", "").replace("</list>", "")
            env_kwargs = [x.strip() for x in env_kwargs.split(",")]
    return env_kwargs


@dataclass
class EnvConfig:
    env_id: str
    num_envs: int
    max_episode_steps: int

    make_env: bool = True

    continuous_task: bool = True

    cat_state: bool = True
    cat_pixels: bool = False
    frame_stack: int = 3

    stationary_base: bool = False
    stationary_torso: bool = False
    stationary_head: bool = True

    task_plan_fp: Optional[str] = None
    spawn_data_fp: Optional[str] = None

    record_video: bool = True
    debug_video: bool = False
    debug_video_gen: bool = False
    save_video_freq: Optional[int] = None
    info_on_video: bool = True

    extra_stat_keys: Union[List[str], str] = field(default_factory=list)
    env_kwargs: Dict = field(default_factory=dict)

    def __post_init__(self):
        self.extra_stat_keys = recursive_fix_env_kwargs(self.extra_stat_keys)
        self.env_kwargs = recursive_fix_env_kwargs(self.env_kwargs)


def make_env(
    env_cfg: EnvConfig,
    video_path: Optional[Union[str, Path]] = None,
    wrappers: List[gym.Wrapper] = [],
):
    if env_cfg.task_plan_fp is not None:
        plan_data = plan_data_from_file(env_cfg.task_plan_fp)
        env_cfg.env_kwargs["task_plans"] = env_cfg.env_kwargs.pop(
            "task_plans", plan_data.plans
        )
        env_cfg.env_kwargs["scene_builder_cls"] = env_cfg.env_kwargs.pop(
            "scene_builder_cls", plan_data.dataset
        )
    if env_cfg.spawn_data_fp is not None:
        env_cfg.env_kwargs["spawn_data_fp"] = env_cfg.spawn_data_fp
    env = gym.make(
        env_cfg.env_id,
        max_episode_steps=env_cfg.max_episode_steps,
        obs_mode="rgbd",
        reward_mode="normalized_dense",
        control_mode="pd_joint_delta_pos",
        render_mode="all",
        shader_dir="minimal",
        robot_uids="fetch",
        num_envs=env_cfg.num_envs,
        sim_backend="gpu",
        **env_cfg.env_kwargs,
    )

    for wrapper in wrappers:
        env = wrapper(env)

    env = FetchDepthObservationWrapper(
        env, cat_state=env_cfg.cat_state, cat_pixels=env_cfg.cat_pixels
    )
    env = FrameStack(
        env,
        num_stack=env_cfg.frame_stack,
        stacking_keys=(
            ["all_depth"]
            if env_cfg.cat_pixels
            else ["fetch_head_depth", "fetch_hand_depth"]
        ),
    )

    if env_cfg.record_video:
        if env_cfg.debug_video:
            env = RecordVideoGPU(
                env,
                output_dir=video_path,
                save_trajectory=False,
                video_fps=20,
                info_on_video=True,
                debug_video_gen=env_cfg.debug_video_gen,
            )
        else:
            save_video_trigger = (
                None
                if env_cfg.save_video_freq is None
                else (
                    lambda x: (x // env_cfg.max_episode_steps) % env_cfg.save_video_freq
                    == 0
                )
            )
            env = RecordEpisode(
                env,
                output_dir=video_path,
                save_trajectory=False,
                max_steps_per_video=env_cfg.max_episode_steps,
                save_video_trigger=save_video_trigger,
                avoid_overwriting_video=True,
                video_fps=20,
                info_on_video=env_cfg.info_on_video,
            )

    env = FetchActionWrapper(
        env,
        stationary_base=env_cfg.stationary_base,
        stationary_torso=env_cfg.stationary_torso,
        stationary_head=env_cfg.stationary_head,
    )

    venv = ManiSkillVectorEnv(
        env,
        max_episode_steps=env_cfg.max_episode_steps,
        ignore_terminations=env_cfg.continuous_task,
    )
    venv = VectorRecordEpisodeStatistics(
        venv,
        max_episode_steps=env_cfg.max_episode_steps,
        extra_stat_keys=env_cfg.extra_stat_keys,
    )

    return venv
