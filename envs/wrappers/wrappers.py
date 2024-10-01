import gymnasium as gym


class FetchActionWrapper(gym.ActionWrapper):
    def __init__(
        self, env, stationary_base=False, stationary_torso=False, stationary_head=True
    ):
        self._stationary_base = stationary_base
        self._stationary_torso = stationary_torso
        self._stationary_head = stationary_head
        super().__init__(env)

    def action(self, action):
        if self._stationary_base:
            action[..., -1] = 0
            action[..., -2] = 0
        if self._stationary_torso:
            action[..., -3] = 0
        if self._stationary_head:
            action[..., -4] = 0
            action[..., -5] = 0
        return action


class ContinuousTaskWrapper(gym.Wrapper):
    def __init__(self, env):
        super().__init__(env)
        self.success_once = False

    def reset(self, *args, **kwargs):
        self.success_once = False
        return super().reset(*args, **kwargs)

    def step(self, action, *args, **kwargs):
        obs, rew, _, trunc, info = super().step(action, *args, **kwargs)
        self.success_once = self.success_once or info["success"]
        info["stats"] = dict(
            success_at_end=int(info["success"]),
            success=self.success_once,
        )
        return obs, rew, False, trunc, info


class EpisodicTaskWrapper(gym.Wrapper):
    def __init__(self, env) -> None:
        super().__init__(env)

    def reset(self, *, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)
        self.success_once = False
        return obs, info

    def step(self, action):
        observation, reward, terminated, truncated, info = super().step(action)
        if info["success"]:
            terminated = True
        return observation, reward, terminated, truncated, info


class EpisodeStatsWrapper(gym.Wrapper):
    """
    Adds additional info useful for curriculums
    """

    def reset(self, *, seed=None, options=None):
        self.eps_seed = seed
        obs, info = super().reset(seed=seed, options=options)
        self.eps_ret = 0
        self.eps_len = 0
        self.success_once = False
        return obs, info

    def step(self, action):
        observation, reward, terminated, truncated, info = super().step(action)
        self.eps_ret += reward
        self.eps_len += 1
        info["eps_ret"] = self.eps_ret
        info["eps_len"] = self.eps_len
        info["seed"] = self.eps_seed
        self.success_once = self.success_once | info["success"]
        info["stats"] = dict(
            success_at_end=int(info["success"]),
            success=self.success_once,
        )
        return observation, reward, terminated, truncated, info
