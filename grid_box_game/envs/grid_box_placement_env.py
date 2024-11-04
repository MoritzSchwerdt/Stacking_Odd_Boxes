from gymnasium import Env, spaces
from gymnasium.utils import seeding
import numpy as np
from .grid_box_game import GridBoxGame

class GridBoxPlacementEnv(Env):
    metadata = {'render_modes': ['human', 'rgb_array'], 'render_fps': 60}

    def __init__(self, render_mode=None):
        super(GridBoxPlacementEnv, self).__init__()
        self.game = None  # Will be initialized in reset()
        self.render_mode = render_mode  # Set the render mode
        self.action_space = spaces.Discrete(6)

        # Observation space: Flattened grid plus current box position and size
        grid_size = 5 * 5
        obs_low = np.zeros(grid_size + 4, dtype=int)
        obs_high = np.ones(grid_size + 4, dtype=int)
        max_position = 4
        max_size = 5
        obs_high[grid_size] = max_position  # current_box_x
        obs_high[grid_size + 1] = max_position  # current_box_y
        obs_high[grid_size + 2] = max_size  # current_box_width
        obs_high[grid_size + 3] = max_size  # current_box_height
        self.observation_space = spaces.Box(low=obs_low, high=obs_high, dtype=int)

        self._np_random = None
        self.max_steps = 1000
        self.current_step = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self._np_random, seed = seeding.np_random(seed)
        # Initialize the game with the random number generator
        self.game = GridBoxGame(np_random=self._np_random, render_mode=self.render_mode)
        obs_dict = self.game.reset()
        obs = self._flatten_obs(obs_dict)
        info = {}
        return obs, info

    def step(self, action):
        self.current_step += 1
        reward = self.game.action(action)
        obs_dict = self.game.observe()
        obs = self._flatten_obs(obs_dict)
        terminated = self.game.is_done()
        info = {}
        truncated = self.current_step >= self.max_steps

        return obs, reward, terminated, truncated, info

    def render(self):
        return self.game.render(mode=self.render_mode)

    def close(self):
        self.game.close()

    def _flatten_obs(self, obs_dict):
        grid_flat = obs_dict['grid'].flatten()
        obs = np.concatenate([
            grid_flat,
            obs_dict['current_box_position'],
            obs_dict['current_box_size']
        ])
        return obs
