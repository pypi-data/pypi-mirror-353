"""
服务区饱和度分析系统 - 流量分析模块API

提供用于流量分析的专门API函数。
"""

import os
import pathlib
import pandas as pd
import numpy as np
from typing import Dict, Optional, Union, List, Tuple
import logging

from saturation.flow import (
    create_merged_flow_file, 
    calculate_time_values,
    adjust_flow,
    calculate_flow,
    calculate_inner_outer_flow,
    calculate_vehicle_type_flow,
    main as flow_main
)

# 配置日志
logger = logging.getLogger(__name__)

def get_data_dir():
    """获取数据目录的绝对路径"""
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent.absolute()
    # 项目根目录
    project_root = current_dir.parent
    # 数据目录
    data_dir = os.path.join(project_root, "result")
    return data_dir

def analyze_vehicle_flow(input_file: str, 
                       output_file: Optional[str] = None,
                       data_dir: Optional[str] = None) -> str:
    """
    分析车辆流量
    
    Args:
        input_file: 输入文件名
        output_file: 输出文件名（可选）
        data_dir: 数据目录路径（可选）
        
    Returns:
        str: 输出文件路径
    """
    logger.info(f"开始分析车辆流量，输入文件: {input_file}")
    
    if data_dir is None:
        data_dir = get_data_dir()
    
    # 确保目录存在
    os.makedirs(data_dir, exist_ok=True)
    
    # 调用原始函数
    result_path = calculate_flow(
        input_filename=input_file,
        output_filename=output_file if output_file else "flow_analysis.csv"
    )
    
    logger.info(f"车辆流量分析完成，结果保存在: {result_path}")
    return result_path

def analyze_inner_outer_flow(input_file: str, 
                          inner_file: Optional[str] = "inner.csv",
                          outer_file: Optional[str] = "outer.csv",
                          data_dir: Optional[str] = None) -> Tuple[str, str]:
    """
    分析内部和外部流量
    
    Args:
        input_file: 输入文件名
        inner_file: 内部流量输出文件名（可选）
        outer_file: 外部流量输出文件名（可选）
        data_dir: 数据目录路径（可选）
        
    Returns:
        Tuple[str, str]: (内部流量文件路径, 外部流量文件路径)
    """
    logger.info(f"开始分析内部和外部流量，输入文件: {input_file}")
    
    if data_dir is None:
        data_dir = get_data_dir()
    
    # 确保目录存在
    os.makedirs(data_dir, exist_ok=True)
    
    # 调用原始函数
    inner_path, outer_path = calculate_inner_outer_flow(
        input_filename=input_file,
        inner_filename=inner_file,
        outer_filename=outer_file
    )
    
    logger.info(f"内部和外部流量分析完成")
    logger.info(f"内部流量保存在: {inner_path}")
    logger.info(f"外部流量保存在: {outer_path}")
    
    return inner_path, outer_path

def analyze_vehicle_type_flow(input_file: str,
                           ke_inner_file: Optional[str] = "etc_ke_inner.csv",
                           ke_outer_file: Optional[str] = "etc_ke_outer.csv",
                           huo_inner_file: Optional[str] = "etc_huo_inner.csv",
                           huo_outer_file: Optional[str] = "etc_huo_outer.csv",
                           data_dir: Optional[str] = None) -> Tuple[str, str, str, str]:
    """
    按车辆类型分析内外流量
    
    Args:
        input_file: 输入文件名
        ke_inner_file: 内部客车流量输出文件名（可选）
        ke_outer_file: 外部客车流量输出文件名（可选）
        huo_inner_file: 内部货车流量输出文件名（可选）
        huo_outer_file: 外部货车流量输出文件名（可选）
        data_dir: 数据目录路径（可选）
        
    Returns:
        Tuple[str, str, str, str]: (内部客车流量文件路径, 外部客车流量文件路径, 
                               内部货车流量文件路径, 外部货车流量文件路径)
    """
    logger.info(f"开始按车辆类型分析内外流量，输入文件: {input_file}")
    
    if data_dir is None:
        data_dir = get_data_dir()
    
    # 确保目录存在
    os.makedirs(data_dir, exist_ok=True)
    
    # 调用原始函数
    ke_inner_path, ke_outer_path, huo_inner_path, huo_outer_path = calculate_vehicle_type_flow(
        input_filename=input_file,
        ke_inner_filename=ke_inner_file,
        ke_outer_filename=ke_outer_file,
        huo_inner_filename=huo_inner_file,
        huo_outer_filename=huo_outer_file
    )
    
    logger.info(f"车辆类型内外流量分析完成")
    
    return ke_inner_path, ke_outer_path, huo_inner_path, huo_outer_path

def create_flow_input_file(output_file: Optional[str] = "flow-kehuo-adjusted.xlsx",
                        data_dir: Optional[str] = None) -> str:
    """
    创建用于预测模型的输入流量文件
    
    Args:
        output_file: 输出文件名（可选）
        data_dir: 数据目录路径（可选）
        
    Returns:
        str: 输出文件路径
    """
    logger.info(f"开始创建用于预测模型的输入流量文件")
    
    if data_dir is None:
        data_dir = get_data_dir()
    
    # 确保目录存在
    os.makedirs(data_dir, exist_ok=True)
    
    # 调用原始函数
    result_path = create_merged_flow_file(output_filename=output_file)
    
    logger.info(f"输入流量文件创建完成，保存在: {result_path}")
    return result_path

def run_flow_analysis_pipeline(data_dir: Optional[str] = None) -> Dict[str, str]:
    """
    运行完整的流量分析流程
    
    Args:
        data_dir: 数据目录路径（可选）
        
    Returns:
        Dict[str, str]: 包含各步骤结果文件路径的字典
    """
    logger.info(f"开始完整的流量分析流程")
    
    if data_dir is None:
        data_dir = get_data_dir()
    
    # 确保目录存在
    os.makedirs(data_dir, exist_ok=True)
    
    # 调用原始主函数
    results = flow_main()
    
    logger.info(f"完整流量分析流程完成")
    
    return results 