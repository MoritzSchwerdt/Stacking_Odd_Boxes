import os
import gymnasium as gym
from stable_baselines3 import PPO
from envs.grid_box_placement_env import GridBoxPlacementEnv

def video_trigger(episode_id):
    N = 100  # Record every 100th episode
    return episode_id % N == 0

def main():
    # Folder to Create Vids
    video_folder = 'box_stacking/videos'
    os.makedirs(video_folder, exist_ok=True)

    # Create env
    env = GridBoxPlacementEnv(render_mode='rgb_array')
    env = gym.wrappers.RecordVideo(
        env,
        video_folder=video_folder,
        episode_trigger=video_trigger,
        name_prefix="training_video"
    )

    # Create model
    model = PPO('MlpPolicy', env, verbose=0, tensorboard_log='box_stacking/tensorboard/')
    total_timesteps = 300000

    # Train model
    model.learn(total_timesteps=total_timesteps)

    # Save model
    model.save("box_stacking/ppo_grid_box_placement")

    # Close the environment
    env.close()

if __name__ == "__main__":
    main()
