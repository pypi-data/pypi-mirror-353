"""
服务区饱和度分析系统 - 预测模块API

提供用于饱和度预测的专门API函数。
"""

import os
import pathlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Optional, Union, List, Tuple
import logging

from saturation.pre.预测模型 import (
    predict_saturation,
    main as prediction_main
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

def predict_future_saturation(input_file: str, 
                           output_model: str = "saturation_model.h5",
                           train_size: int = 200, 
                           time_steps: int = 5, 
                           input_dims: int = 6, 
                           lstm_units: int = 64,
                           epochs: int = 100,
                           batch_size: int = 64,
                           save_plot: bool = True,
                           data_dir: Optional[str] = None) -> Dict:
    """
    预测未来饱和度
    
    Args:
        input_file: 输入文件名
        output_model: 输出模型文件名
        train_size: 训练集大小
        time_steps: 时间步长
        input_dims: 输入维度
        lstm_units: LSTM单元数量
        epochs: 训练轮数
        batch_size: 批大小
        save_plot: 是否保存图表
        data_dir: 数据目录路径（可选）
        
    Returns:
        Dict: 包含预测结果和评估指标的字典
    """
    logger.info(f"开始预测未来饱和度，输入文件: {input_file}")
    
    if data_dir is None:
        data_dir = get_data_dir()
    
    # 确保目录存在
    os.makedirs(data_dir, exist_ok=True)
    
    # 调用原始函数
    result = predict_saturation(
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
    
    if result:
        logger.info(f"饱和度预测完成")
        logger.info(f"评估指标: RMSE={result['rmse']:.4f}, MAE={result['mae']:.4f}, MAPE={result['mape']:.2f}%")
    else:
        logger.error("饱和度预测失败")
    
    return result

def load_model_and_predict(model_file: str, 
                         input_file: str,
                         time_steps: int = 5,
                         data_dir: Optional[str] = None) -> pd.DataFrame:
    """
    加载已有模型并进行预测
    
    Args:
        model_file: 模型文件名
        input_file: 输入文件名
        time_steps: 时间步长
        data_dir: 数据目录路径（可选）
        
    Returns:
        pd.DataFrame: 包含预测结果的DataFrame
    """
    logger.info(f"加载模型并进行预测，模型文件: {model_file}, 输入文件: {input_file}")
    
    try:
        from keras.models import load_model
        import pandas as pd
        import numpy as np
        
        if data_dir is None:
            data_dir = get_data_dir()
        
        # 确保目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 构建文件路径
        model_path = os.path.join(data_dir, model_file)
        input_path = os.path.join(data_dir, input_file)
        
        # 加载模型
        model = load_model(model_path)
        
        # 加载数据
        data = pd.read_excel(input_path) if input_file.endswith('.xlsx') else pd.read_csv(input_path)
        
        # 记录最大最小值用于反归一化
        g1 = max(data['flow']) if 'flow' in data.columns else 1
        g2 = min(data['flow']) if 'flow' in data.columns else 0
        
        # 归一化处理
        data_normalized = (data - data.min()) / (data.max() - data.min())
        
        # 处理极端值
        data_normalized = data_normalized.replace([np.inf, -np.inf], np.nan)
        data_normalized = data_normalized.fillna(0)
        
        # 创建预测数据
        test_data = data_normalized.values
        
        # 构建输入序列 (简化处理，实际应用可能需要更复杂的处理)
        X = []
        for i in range(len(test_data) - time_steps):
            X.append(test_data[i:(i + time_steps), :])
        
        X = np.array(X)
        
        # 预测
        predicted = model.predict(X)
        
        # 反归一化
        predicted = predicted * (g1 - g2) + g2
        
        # 创建结果DataFrame
        result_df = pd.DataFrame({
            'time_step': range(len(predicted)),
            'predicted_t': predicted[:, 0],
            'predicted_t+1': predicted[:, 1]
        })
        
        logger.info("预测完成")
        return result_df
    
    except Exception as e:
        logger.error(f"预测过程中出错: {str(e)}")
        return pd.DataFrame()

def run_prediction_with_custom_params(input_file: str, 
                                    output_prefix: str = "custom_",
                                    model_params: Dict = None,
                                    training_params: Dict = None,
                                    data_dir: Optional[str] = None) -> Dict:
    """
    使用自定义参数运行预测
    
    Args:
        input_file: 输入文件名
        output_prefix: 输出文件前缀
        model_params: 模型参数（可选）
        training_params: 训练参数（可选）
        data_dir: 数据目录路径（可选）
        
    Returns:
        Dict: 包含预测结果和评估指标的字典
    """
    logger.info(f"使用自定义参数进行预测，输入文件: {input_file}")
    
    # 默认参数
    default_model_params = {
        'time_steps': 5,
        'input_dims': 6,
        'lstm_units': 64
    }
    
    default_training_params = {
        'train_size': 200,
        'epochs': 100,
        'batch_size': 64
    }
    
    # 使用提供的参数覆盖默认参数
    if model_params:
        default_model_params.update(model_params)
    
    if training_params:
        default_training_params.update(training_params)
    
    # 构建输出模型文件名
    output_model = f"{output_prefix}saturation_model.h5"
    
    # 调用预测函数
    return predict_future_saturation(
        input_file=input_file,
        output_model=output_model,
        time_steps=default_model_params['time_steps'],
        input_dims=default_model_params['input_dims'],
        lstm_units=default_model_params['lstm_units'],
        train_size=default_training_params['train_size'],
        epochs=default_training_params['epochs'],
        batch_size=default_training_params['batch_size'],
        data_dir=data_dir
    ) 