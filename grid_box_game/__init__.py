from gymnasium.envs.registration import register

from .envs import GridBoxGame, GridBoxPlacementEnv


register(
    id='BoxStacker-v0',
    entry_point='gym_game.envs:CustomEnv',
    max_episode_steps=1000,
)