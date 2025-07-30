"""
文件操作工具

提供文件路径处理相关的实用函数。
"""

import os
import pathlib
from typing import Optional, Union


def ensure_dir_exists(dir_path: str) -> str:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        dir_path (str): 目录路径
        
    Returns:
        str: 目录路径
    """
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def get_absolute_path(file_path: str, base_dir: Optional[str] = None) -> str:
    """
    获取文件的绝对路径
    
    如果提供的路径已经是绝对路径，则直接返回
    如果是相对路径，则基于base_dir构建绝对路径
    
    Args:
        file_path (str): 文件路径
        base_dir (str, optional): 基础目录，默认为当前工作目录
        
    Returns:
        str: 文件的绝对路径
    """
    if os.path.isabs(file_path):
        return file_path
        
    if base_dir is None:
        base_dir = os.getcwd()
        
    return os.path.abspath(os.path.join(base_dir, file_path))


def is_valid_file(file_path: str) -> bool:
    """
    检查文件是否存在且可读
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        bool: 如果文件存在且可读则返回True，否则返回False
    """
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)


def join_paths(base_dir: str, *paths: str) -> str:
    """
    连接多个路径组件
    
    Args:
        base_dir (str): 基础目录
        *paths: 其他路径组件
        
    Returns:
        str: 连接后的路径
    """
    result = base_dir
    for path in paths:
        result = os.path.join(result, path)
    return result 