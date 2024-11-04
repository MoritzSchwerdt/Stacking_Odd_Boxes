import numpy as np
import robosuite as suite
from robosuite.wrappers import GymWrapper
from stable_baselines3 import A2C, DQN
from stable_baselines3 import HER, SAC, DDPG, TD3
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.vec_env import DummyVecEnv, VecVideoRecorder
from stable_baselines3.common.logger import configure
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor
import os

# Define a custom GymWrapper with render_mode attribute and flipped frames
class CustomGymWrapper(GymWrapper):
    def __init__(self, env, render_mode="rgb_array"):
        super().__init__(env)
        self.metadata = {"render.modes": ["rgb_array"], "semantics.async": True}
        self.render_mode = render_mode

    def render(self, mode="rgb_array"):
        if mode == "rgb_array":
            # Capture and flip the frame vertically
            frame = self.env.sim.render(width=500, height=500, camera_name="frontview")
            return np.flipud(frame)  # Flip the frame vertically
        else:
            raise ValueError(f"Unsupported render mode: {mode}")

# Function to create a new instance of the environment
def make_env():
    env_rb = suite.make(
        env_name="Stack",
        robots="Panda",
        has_renderer=False,  # Disable on-screen rendering
        has_offscreen_renderer=True,  # Enable off-screen rendering only
        use_camera_obs=False,
        reward_shaping=True,
    )
    env = CustomGymWrapper(env_rb, render_mode="rgb_array")
    return Monitor(env)

# Set up directories for logs and videos
log_path = "./tensorboard_logs/"
video_folder = "videos/"
os.makedirs(log_path, exist_ok=True)
os.makedirs(video_folder, exist_ok=True)

# Create multiple environment instances for DummyVecEnv
num_envs = 1  # Number of environments to run in parallel
env_fns = [make_env for _ in range(num_envs)]
vec_env = DummyVecEnv(env_fns)

# Configure TensorBoard logging
new_logger = configure(log_path, ["tensorboard"])

# Initialize the model with vec_env and set logger
#model = A2C("MlpPolicy", vec_env, verbose=1)
n_actions = vec_env.action_space.shape[-1]
#action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

model = DDPG("MlpPolicy", vec_env, verbose=1)
model.set_logger(new_logger)

# Wrap the environment with VecVideoRecorder for video recording in evaluations
video_recorder = VecVideoRecorder(
    vec_env,
    video_folder,
    record_video_trigger=lambda x: x % 10_000 == 0,  # Record every 10,000 steps
    video_length=1000,  # Video length in frames
    name_prefix="robot_performance"
)

# Define an evaluation callback to run periodic evaluations
eval_callback = EvalCallback(
    video_recorder,  # Use video_recorder only for evaluation
    best_model_save_path=log_path,
    log_path=log_path,
    eval_freq=10_000,  # Evaluate every 10,000 steps
    deterministic=True,
    render=True,  # Enables rendering during evaluation episodes
)

# Train the model and use callback to capture evaluation episodes with video
model.learn(total_timesteps=200_000, callback=eval_callback)

# Clean up
video_recorder.close()
vec_env.close()
