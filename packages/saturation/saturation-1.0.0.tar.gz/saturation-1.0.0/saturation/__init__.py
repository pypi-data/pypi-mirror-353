"""
服务区饱和度分析系统

该包提供一系列工具和模型用于高速公路服务区饱和度分析，包括：
- 数据处理
- 聚类分析
- 分类判别
- 流量分析
- 饱和度分析
- 预测模型

包含多个可以独立调用的功能模块。
"""

__version__ = '1.0.0'

# 导入主要接口
from saturation.flow import main as flow_analysis
from saturation.enJud import data_process, julei, fenleipanbie, panbie, yuzhi, huo_canshu
from saturation.satAna import saturation as saturation_analysis
from saturation.pre import 预测模型 as prediction_model

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

__all__ = [
    'process_data', 
    'calculate_threshold',
    'cluster_analysis', 
    'classification_analysis',
    'speed_classification',
    'truck_parameter_analysis',
    'flow_analysis',
    'analyze_saturation',
    'predict_saturation',
    'get_data_dir'
] 