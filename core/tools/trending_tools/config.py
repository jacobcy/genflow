"""配置管理模块

从环境变量读取配置信息。
"""
import os
from typing import Dict
from pathlib import Path

def get_config() -> Dict:
    """获取配置信息

    从环境变量读取:
    - DAILY_HOT_API_URL: API服务地址
    - REDIS_HOST: Redis主机地址
    - REDIS_PORT: Redis端口
    - REDIS_DB: Redis数据库编号
    - REDIS_PASSWORD: Redis密码(可选)
    - PLATFORM_CONFIG_PATH: 平台配置文件路径
    - CONFIG_UPDATE_INTERVAL: 配置更新间隔(秒)
    """
    redis_url = "redis://"
    if os.getenv("REDIS_PASSWORD"):
        redis_url += f":{os.getenv('REDIS_PASSWORD')}@"
    redis_url += f"{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}"
    redis_url += f"/{os.getenv('REDIS_DB', '0')}"

    # 获取项目根目录
    root_dir = Path(__file__).parent.parent.parent.parent

    return {
        "api_base_url": os.getenv("DAILY_HOT_API_URL", "http://localhost:6688"),
        "redis_url": redis_url,
        "platform_config_path": os.getenv("PLATFORM_CONFIG_PATH", str(root_dir / "data/platform_config.json")),
        "config_update_interval": int(os.getenv("CONFIG_UPDATE_INTERVAL", str(7 * 24 * 3600)))  # 默认7天
    }
