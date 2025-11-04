# 临时测试脚本
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"当前脚本目录: {current_dir}")

# 计算.env.dev文件的正确路径
env_file_path = os.path.join(current_dir, "../.env.dev")
print(f"Env文件路径: {env_file_path}")
print(f"Env文件是否存在: {os.path.exists(env_file_path)}")

# 测试从backend/app/core/config.py的路径
config_dir = os.path.join(current_dir, "app/core")
config_env_path = os.path.join(config_dir, "../../../.env.dev")
print(f"从config.py计算的Env文件路径: {config_env_path}")
print(f"从config.py计算的Env文件是否存在: {os.path.exists(config_env_path)}")