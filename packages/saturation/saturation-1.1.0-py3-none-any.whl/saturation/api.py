"""
服务区饱和度分析系统 - API接口

提供简化的函数接口，允许用户轻松调用系统各个组件。
该模块主要作为各功能模块的统一入口点，整合了数据处理、分析和预测功能。
"""

import os
import pathlib
import logging
from typing import Dict, Optional, Tuple, Union, List
import pandas as pd

from saturation.enJud import data_process
from saturation.enJud import julei
from saturation.enJud import fenleipanbie
from saturation.enJud import panbie
from saturation.enJud import yuzhi
from saturation.enJud import huo_canshu
from saturation import flow
from saturation.satAna import saturation
from saturation.pre import 预测模型 as prediction_model

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def configure_data_directory(data_dir: Optional[str] = None) -> str:
    """
    配置数据目录路径
    
    如果提供了data_dir参数，将使用该路径作为数据目录
    否则将使用默认的项目根目录下的data目录
    
    Args:
        data_dir: 数据目录的路径（可选）
        
    Returns:
        str: 配置好的数据目录路径
    """
    if data_dir is None:
        # 使用默认路径
        current_dir = pathlib.Path(__file__).parent.absolute()
        project_root = current_dir.parent
        data_dir = os.path.join(project_root, "result")
    
    # 确保目录存在
    os.makedirs(data_dir, exist_ok=True)
    logger.info(f"数据目录已配置为: {data_dir}")
    
    return data_dir

def process_raw_data(input_file: str, data_dir: Optional[str] = None, 
                   output_file: Optional[str] = None) -> str:
    """
    处理原始数据
    
    Args:
        input_file: 输入文件名或路径
        data_dir: 数据目录路径（可选）
        output_file: 输出文件名（可选）
        
    Returns:
        str: 处理后的文件路径
    """
    logger.info("开始处理原始数据...")
    
    # 如果提供了data_dir，就使用它，否则使用默认路径
    if data_dir is not None:
        # 临时重定向数据目录
        original_get_data_dir = data_process.get_data_dir
        data_process.get_data_dir = lambda: data_dir
    
    # 处理数据
    result_path = data_process.process_initial_data(
        input_filename=input_file, 
        output_filename=output_file if output_file else "processed_data.csv"
    )
    
    # 恢复原来的get_data_dir函数
    if data_dir is not None:
        data_process.get_data_dir = original_get_data_dir
    
    logger.info(f"数据处理完成，结果保存在: {result_path}")
    return result_path

def run_complete_pipeline(input_file: str, data_dir: Optional[str] = None) -> Dict:
    """
    运行完整的分析流程
    
    Args:
        input_file: 输入文件名或路径
        data_dir: 数据目录路径（可选）
        
    Returns:
        Dict: 包含各步骤结果的字典
    """
    logger.info("开始执行完整分析流程...")
    
    # 配置数据目录
    configured_data_dir = configure_data_directory(data_dir)
    
    # 1. 数据处理
    logger.info("步骤1: 数据处理")
    data_process.complete_data_processing_pipeline()
    
    # 2. 聚类分析
    logger.info("步骤2: 聚类分析")
    cluster_result = julei.main()
    
    # 3. 货车参数分析
    logger.info("步骤3: 货车参数分析")
    truck_params = huo_canshu.main()
    
    # 4. 阈值分析
    logger.info("步骤4: 阈值分析")
    threshold = yuzhi.main()
    
    # 5. 速度判别
    logger.info("步骤5: 速度判别")
    speed_result = panbie.main()
    
    # 6. 分类判别分析
    logger.info("步骤6: 分类判别分析")
    classification_result = fenleipanbie.main()
    
    # 7. 流量分析
    logger.info("步骤7: 流量分析")
    flow_result = flow.main()
    
    # 8. 饱和度分析
    logger.info("步骤8: 饱和度分析")
    saturation_result = saturation.main()
    
    # 9. 饱和度预测
    logger.info("步骤9: 饱和度预测")
    prediction_result = prediction_model.main()
    
    logger.info("完整分析流程执行完毕")
    
    # 返回各步骤的结果
    return {
        "data_dir": configured_data_dir,
        "cluster_result": cluster_result,
        "truck_params": truck_params,
        "threshold": threshold,
        "speed_result": speed_result,
        "classification_result": classification_result,
        "flow_result": flow_result,
        "saturation_result": saturation_result,
        "prediction_result": prediction_result
    }

def match_vehicles(up_file: str, down_file: str, output_file: Optional[str] = None, 
                 data_dir: Optional[str] = None) -> str:
    """
    匹配上下行车辆
    
    Args:
        up_file: 上行车辆数据文件名
        down_file: 下行车辆数据文件名
        output_file: 输出文件名（可选）
        data_dir: 数据目录路径（可选）
        
    Returns:
        str: 匹配结果文件路径
    """
    logger.info("开始匹配上下行车辆...")
    
    # 如果提供了data_dir，就使用它，否则使用默认路径
    if data_dir is not None:
        # 临时重定向数据目录
        original_get_data_dir = data_process.get_data_dir
        data_process.get_data_dir = lambda: data_dir
    
    # 匹配车辆
    result_path = data_process.match_vehicles(
        up_filename=up_file,
        down_filename=down_file,
        output_filename=output_file if output_file else "matched_vehicle.csv"
    )
    
    # 恢复原来的get_data_dir函数
    if data_dir is not None:
        data_process.get_data_dir = original_get_data_dir
    
    logger.info(f"车辆匹配完成，结果保存在: {result_path}")
    return result_path

def analyze_flow(input_file: Optional[str] = None, output_file: Optional[str] = None,
               data_dir: Optional[str] = None) -> Dict:
    """
    分析流量
    
    Args:
        input_file: 输入文件名（可选）
        output_file: 输出文件名（可选） 
        data_dir: 数据目录路径（可选）
        
    Returns:
        Dict: 流量分析结果
    """
    logger.info("开始流量分析...")
    
    # 如果提供了data_dir，这里需要考虑如何处理
    # 由于flow.main()没有直接参数，此处实现可能需要进一步修改flow.py
    
    # 分析流量
    flow_result = flow.main()
    
    logger.info("流量分析完成")
    return flow_result

def analyze_saturation_level(ke_flow_file: str, huo_flow_file: str, 
                          output_file: Optional[str] = None,
                          data_dir: Optional[str] = None) -> Tuple[str, str]:
    """
    分析饱和度水平
    
    Args:
        ke_flow_file: 客车流量文件名
        huo_flow_file: 货车流量文件名
        output_file: 输出文件名（可选）
        data_dir: 数据目录路径（可选）
        
    Returns:
        Tuple[str, str]: 饱和度分析结果文件路径和聚类结果文件路径
    """
    logger.info("开始饱和度分析...")
    
    # 如果提供了data_dir，就使用它
    if data_dir is not None:
        # 需要处理saturation模块的数据目录
        pass
    
    # 分析饱和度
    result = saturation.main(
        ke_flow_filename=ke_flow_file,
        huo_flow_filename=huo_flow_file,
        output_filename=output_file if output_file else "saturation_analysis.csv"
    )
    
    logger.info("饱和度分析完成")
    return result

def predict_future_saturation(input_file: str, output_model: str = "saturation_model.h5",
                            train_size: int = 200, time_steps: int = 5,
                            input_dims: int = 6, lstm_units: int = 64,
                            epochs: int = 100, batch_size: int = 64,
                            save_plot: bool = True,
                            data_dir: Optional[str] = None) -> Dict:
    """
    预测未来饱和度
    
    Args:
        input_file: 输入文件名
        output_model: 模型输出文件名
        train_size: 训练集大小
        time_steps: 时间步长
        input_dims: 输入维度
        lstm_units: LSTM单元数量
        epochs: 训练轮数
        batch_size: 批大小
        save_plot: 是否保存图表
        data_dir: 数据目录路径（可选）
        
    Returns:
        Dict: 预测结果
    """
    logger.info("开始预测未来饱和度...")
    
    # 预测
    result = prediction_model.predict_saturation(
        input_filename=input_file,
        output_model=output_model,
        train_size=train_size,
        time_steps=time_steps,
        input_dims=input_dims,
        lstm_units=lstm_units,
        epochs=epochs,
        batch_size=batch_size,
        save_plot=save_plot
    )
    
    logger.info("饱和度预测完成")
    return result 