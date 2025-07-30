"""
配置管理工具

提供全局配置选项管理功能，允许在不同模块间共享配置。
"""

import os
import pathlib
from typing import Any, Dict, Optional

# 默认配置
_DEFAULT_CONFIG = {
    'data_dir': os.path.join(pathlib.Path(__file__).parent.parent.parent.absolute(), "result"),
    'output_dir': os.path.join(pathlib.Path(__file__).parent.parent.parent.absolute(), "result"),
    'model_dir': os.path.join(pathlib.Path(__file__).parent.parent.absolute(), "pre"),
    'debug': False,
    'verbose': True
}

# 当前配置
_CURRENT_CONFIG = _DEFAULT_CONFIG.copy()


def get_config(key: Optional[str] = None) -> Any:
    """
    获取配置值
    
    Args:
        key (str, optional): 配置键名，如果不提供则返回整个配置字典
        
    Returns:
        Any: 配置值或整个配置字典
    """
    if key is None:
        return _CURRENT_CONFIG.copy()
    
    return _CURRENT_CONFIG.get(key, _DEFAULT_CONFIG.get(key))


def set_config(key: str, value: Any) -> None:
    """
    设置配置值
    
    Args:
        key (str): 配置键名
        value (Any): 配置值
    """
    _CURRENT_CONFIG[key] = value
    
    # 如果设置的是目录路径，确保目录存在
    if key.endswith('_dir') and isinstance(value, str):
        os.makedirs(value, exist_ok=True)


def reset_config() -> None:
    """
    重置配置为默认值
    """
    global _CURRENT_CONFIG
    _CURRENT_CONFIG = _DEFAULT_CONFIG.copy()


def update_config(config_dict: Dict[str, Any]) -> None:
    """
    批量更新配置
    
    Args:
        config_dict (Dict[str, Any]): 配置字典
    """
    for key, value in config_dict.items():
        set_config(key, value) 