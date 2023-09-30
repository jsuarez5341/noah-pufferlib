from pdb import set_trace as T
import numpy as np

import gym

import pufferlib
import pufferlib.emulation
import pufferlib.emulation


class ProcgenVecEnv:
    '''WIP Vectorized Procgen environment wrapper
    
    Does not use normal PufferLib emulation'''
    def __init__(self, env_name, num_envs=1,
            num_levels=0, start_level=0,
            distribution_mode="easy"):

        self.num_envs = num_envs
        self.envs = ProcgenEnv(
            env_name=env_name,
            num_envs=num_envs,
            num_levels=num_levels,
            start_level=start_level,
            distribution_mode=distribution_mode,
        )

    @property
    def single_observation_space(self):
        return self.envs.observation_space['rgb']

    @property
    def single_action_space(self):
        return self.envs.action_space

    def reset(self, seed=None):
        obs = self.envs.reset()['rgb']
        rewards = [0] * self.num_envs
        dones = [False] * self.num_envs
        infos = [{}] * self.num_envs
        return obs, rewards, dones, infos

    def step(self, actions):
        actions = np.array(actions)
        obs, rewards, dones, infos = self.envs.step(actions)
        return obs['rgb'], rewards, dones, infos


class ProcgenPostprocessor(pufferlib.emulation.Postprocessor):
    def features(self, obs):
        try:
            return obs['rgb']
        except:
            return obs

    def reward_done_info(self, reward, done, info):
        return float(reward), bool(done), info


def env_creator():
    try:
        with pufferlib.utils.Suppress():
            import procgen
            return gym.make
            #import gym3
            #from procgen.env import ProcgenGym3Env
            #return ProcgenGym3Env
    except:
        raise pufferlib.utils.SetupError('procgen')

def make_env(name='bigfish'):
    '''Atari creation function with default CleanRL preprocessing based on Stable Baselines3 wrappers'''
    env = env_creator()(
        f'procgen-{name}-v0',
        num_levels=0,
        start_level=0,
        paint_vel_info=False,
        use_generated_assets=False,
        center_agent=True,
        use_sequential_levels=False,
        distribution_mode="easy",
    )
 
    # Note: CleanRL normalizes and clips rewards
    #import gym3
    #env = gym3.ToGymEnv(env)
    #env = gym.wrappers.TransformObservation(env, lambda obs: obs["rgb"])
    env = gym.wrappers.RecordEpisodeStatistics(env)
    env = gym.wrappers.NormalizeReward(env, gamma=0.999)
    env = gym.wrappers.TransformReward(env, lambda reward: np.clip(reward, -10, 10))
    env = pufferlib.emulation.GymPufferEnv(
        env=env,
        postprocessor_cls=ProcgenPostprocessor,
    )
    return env
