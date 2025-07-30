"""
服务区饱和度分析系统

该包提供一系列工具和模型用于高速公路服务区饱和度分析，包括：
- 数据处理
- 聚类分析
- 分类判别
- 流量分析
- 饱和度分析
- 预测模型

主要功能模块可以独立调用，也可以通过统一的API接口使用。
"""

__version__ = '1.0.0'

# 导入主要接口
from saturation.flow import main as flow_analysis
from saturation.enJud import data_process, julei, fenleipanbie, panbie, yuzhi, huo_canshu
from saturation.satAna import saturation as saturation_analysis
from saturation.pre import 预测模型 as prediction_model

# 从api和专用API模块导入高级函数
from saturation.api import (
    configure_data_directory,
    process_raw_data,
    run_complete_pipeline,
    match_vehicles,
    analyze_flow,
    analyze_saturation_level,
    predict_future_saturation
)

# 从flow_api导入流量分析专用函数
from saturation.flow_api import (
    analyze_inner_outer_flow,
    analyze_vehicle_type_flow,
    analyze_flow_by_time,
    get_flow_statistics
)

# 从prediction_api导入预测专用函数
from saturation.prediction_api import (
    predict_future_saturation as predict_saturation_advanced,
    load_model_and_predict,
    run_prediction_with_custom_params,
    evaluate_model_performance
)

# 建立简洁的API
process_data = data_process.complete_data_processing_pipeline
calculate_threshold = yuzhi.calculate_threshold
cluster_analysis = julei.main
classification_analysis = fenleipanbie.main
speed_classification = panbie.main
truck_parameter_analysis = huo_canshu.main
flow_analysis = flow_analysis
analyze_saturation = saturation_analysis.main
predict_saturation = prediction_model.main

# 便利函数，返回项目数据目录路径
def get_data_dir():
    """获取数据目录的绝对路径"""
    return data_process.get_data_dir()

# 设置默认输出目录函数
def set_output_dir(output_dir):
    """设置全局输出目录
    
    Args:
        output_dir (str): 输出目录的路径
        
    Returns:
        str: 配置后的输出目录路径
    """
    return configure_data_directory(output_dir)

__all__ = [
    # 基础API
    'process_data', 
    'calculate_threshold',
    'cluster_analysis', 
    'classification_analysis',
    'speed_classification',
    'truck_parameter_analysis',
    'flow_analysis',
    'analyze_saturation',
    'predict_saturation',
    'get_data_dir',
    'set_output_dir',
    
    # 高级API
    'configure_data_directory',
    'process_raw_data',
    'run_complete_pipeline',
    'match_vehicles',
    'analyze_flow',
    'analyze_saturation_level',
    'predict_future_saturation',
    
    # 流量专用API
    'analyze_inner_outer_flow',
    'analyze_vehicle_type_flow',
    'analyze_flow_by_time',
    'get_flow_statistics',
    
    # 预测专用API
    'predict_saturation_advanced',
    'load_model_and_predict',
    'run_prediction_with_custom_params',
    'evaluate_model_performance'
] 