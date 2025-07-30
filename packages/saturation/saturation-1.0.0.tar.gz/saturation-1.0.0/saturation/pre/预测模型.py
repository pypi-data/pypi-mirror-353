#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务区饱和度分析系统 - 预测模块
"""
import os
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.layers import Input, Dense, LSTM, Conv1D, Dropout, Bidirectional, Multiply
from keras.layers import Flatten, Lambda, RepeatVector, Permute, Reshape
from keras.models import Model, load_model
from keras import backend as K
from sklearn.metrics import mean_squared_error, mean_absolute_error
from packaging import version
import sklearn

def get_data_dir():
    """获取数据目录的绝对路径"""
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent.absolute()
    # 向上两级获取项目根目录
    project_root = current_dir.parent.parent
    # 数据目录
    data_dir = os.path.join(project_root, "result")
    return data_dir

# 注意力机制函数
def attention_block_3(inputs):            
    # 获取输入形状 - 兼容不同版本的Keras
    try:
        # 尝试使用K.int_shape (较老版本Keras)
        feature_cnt = K.int_shape(inputs)[1]
        dim = K.int_shape(inputs)[2]
    except AttributeError:
        # 较新版本Keras
        feature_cnt = inputs.shape[1]
        dim = inputs.shape[2]
        
    h_block = int(feature_cnt*dim/64/2)
    hidden = Flatten()(inputs)
    while(h_block >= 1):
        h_dim = h_block * 64
        hidden = Dense(h_dim, activation='selu', use_bias=True)(hidden)
        h_block = int(h_block/2)
    attention = Dense(feature_cnt, activation='softmax', name='attention')(hidden)
    attention = RepeatVector(dim)(attention)
    attention = Permute((2, 1))(attention)
    
    attention_out = Multiply()([attention, inputs])
    return attention_out

def attention_block_4(inputs):   #求和
    # 获取输入形状 - 兼容不同版本的Keras
    try:
        # 尝试使用K.int_shape (较老版本Keras)
        feature_cnt = K.int_shape(inputs)[1]
        dim = K.int_shape(inputs)[2]
    except AttributeError:
        # 较新版本Keras
        feature_cnt = inputs.shape[1]
        dim = inputs.shape[2]
        
    a = Flatten()(inputs)
    a = Dense(feature_cnt*dim, activation='softmax')(a) 
    a = Reshape((feature_cnt, dim))(a)
    a = Lambda(lambda x: K.sum(x, axis=2), name='attention')(a)
    a = RepeatVector(dim)(a)
    a_probs = Permute((2, 1), name='attention_vec')(a)
    attention_out = Multiply()([inputs, a_probs])
    return attention_out

# 创建注意力模型
def attention_model1(time_steps, input_dims, lstm_units):
    inputs = Input(shape=(time_steps, input_dims))

    x = Conv1D(filters=64, kernel_size=1, activation='relu')(inputs)
    x = Dropout(0.3)(x)

    lstm_out = Bidirectional(LSTM(lstm_units, return_sequences=True))(x)
    lstm_out = Dropout(0.3)(lstm_out)
    attention_mul = attention_block_3(lstm_out)
    attention_mul = Flatten()(attention_mul)
    
    attention_mul = Dense(128, activation='sigmoid')(attention_mul)
    attention_mul = Dropout(0.3)(attention_mul)
   
    output = Dense(2, activation='sigmoid')(attention_mul)
    model = Model(inputs=[inputs], outputs=output)
    return model

# 两步数据处理
def create_dataset2(dataset, look_back):
    '''对数据进行处理'''
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back - 2):
        a = dataset[i:(i + look_back), :]
        dataX.append(a)
        dataY.append([dataset[i + look_back, :], dataset[i + look_back + 1, :]])
    TrainX = np.array(dataX)
    Train_Y = np.array(dataY)
    return TrainX, Train_Y

# 计算MAPE
def mean_absolute_percentage_error(y_true, y_pred): 
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # 避免除以零的情况
    non_zero = y_true != 0
    mape = np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100
    return mape

# 计算RMSE - 兼容不同版本的scikit-learn
def calculate_rmse(y_true, y_pred):
    """计算RMSE，兼容不同版本的scikit-learn"""
    try:
        # 检查scikit-learn版本
        sklearn_version = version.parse(sklearn.__version__)
        if sklearn_version >= version.parse('0.22.0'):
            # 新版本直接支持squared=False参数
            return mean_squared_error(y_true, y_pred, squared=False)
        else:
            # 旧版本需要手动计算平方根
            return np.sqrt(mean_squared_error(y_true, y_pred))
    except Exception:
        # 发生任何错误时使用最安全的方法
        return np.sqrt(mean_squared_error(y_true, y_pred))

def predict_saturation(input_filename="flow-kehuo-adjusted.xlsx", 
                      output_model="saturation_model.h5",
                      train_size=200, 
                      time_steps=5, 
                      input_dims=6, 
                      lstm_units=64,
                      epochs=100,
                      batch_size=64,
                      save_plot=True):
    """饱和度预测主函数"""
    data_dir = get_data_dir()
    
    # 文件路径
    input_path = os.path.join(data_dir, input_filename)
    model_path = os.path.join(data_dir, output_model)
    
    # 加载数据
    try:
        data = pd.read_excel(input_path)
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {input_path}")
        return None
        
    # 确保有需要的列
    required_columns = ['flow', 'etc_flow', 'etc_ke', 'etc_huo', 'inner', 'outer']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        print(f"错误：输入文件缺少必要的列: {', '.join(missing_columns)}")
        # 使用可用的列
        available_columns = [col for col in required_columns if col in data.columns]
        if len(available_columns) >= 2:
            print(f"使用可用的列: {', '.join(available_columns)}")
            data = data[available_columns]
            input_dims = len(available_columns)
        else:
            print("可用的列不足，无法继续分析")
            return None
    else:
        # 只选择需要的列
        data = data[required_columns]
    
    # 记录最大最小值用于反归一化
    g1 = max(data['flow'])
    g2 = min(data['flow'])

    # 归一化
    data = (data - data.min()) / (data.max() - data.min())

    # 处理极端值
    data = data.replace([np.inf, -np.inf], np.nan)
    data = data.fillna(0)
    
    # 分割训练集和测试集
    if len(data) <= train_size:
        train_size = int(len(data) * 0.8)  # 如果数据不够，使用80%作为训练集
    
    train = data.iloc[:train_size, :].values
    test = data.iloc[train_size:, :].values

    # 提取目标变量
    train_data = train[:, 0].reshape(len(train), 1)
    test_data = test[:, 0].reshape(len(test), 1)

    # 构建训练数据集
    train_X, _ = create_dataset2(train, time_steps)
    _, train_Y = create_dataset2(train_data, time_steps)
    train_Y = train_Y.reshape(train_Y.shape[0], 2)
    
    # 构建测试数据集
    test_X, _ = create_dataset2(test, time_steps)
    _, test_Y = create_dataset2(test_data, time_steps)
    test_Y = test_Y.reshape(test_Y.shape[0], 2)

    # 创建模型
    model = attention_model1(time_steps, input_dims, lstm_units)
    model.compile(optimizer='adam', loss='mse', run_eagerly=True)
    model.summary()
    
    # 训练模型
    print("开始训练模型...")
    model.fit(train_X, train_Y, batch_size=batch_size, epochs=epochs, validation_split=0.1)
    
    # 保存模型
    model.save(model_path)
    print(f"模型已保存至：{model_path}")
    
    # 预测
    print("进行预测...")
    predicted = model.predict(test_X)
    
    # 反归一化
    y_true = test_Y * (g1 - g2) + g2
    y_pred = predicted * (g1 - g2) + g2
    
    # 计算评估指标
    rmse = calculate_rmse(y_true[:, 1], y_pred[:, 1])
    mae = mean_absolute_error(y_true[:, 1], y_pred[:, 1])
    mape = mean_absolute_percentage_error(y_true[:, 1], y_pred[:, 1])
    
    print("预测评估结果:")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"MAPE: {mape:.2f}%")
    
    # 绘制结果
    if save_plot:
        plt.figure(figsize=(12, 8))
        plt.plot(y_true[:, 0], label='实际值', color='blue', marker='o', markersize=3)
        plt.plot(y_pred[:, 0], label='预测值', color='red', linestyle='--', marker='x', markersize=3)
        plt.title('饱和度预测结果对比')
        plt.xlabel('时间步')
        plt.ylabel('饱和度')
        plt.legend()
        plt.grid(True)
        
        # 保存图表
        plot_path = os.path.join(data_dir, "saturation_prediction.png")
        plt.savefig(plot_path)
        plt.close()
        print(f"预测结果图表已保存至：{plot_path}")

    # 保存预测结果到CSV
    results_df = pd.DataFrame({
        'actual_t': y_true[:, 0],
        'predicted_t': y_pred[:, 0],
        'actual_t+1': y_true[:, 1],
        'predicted_t+1': y_pred[:, 1]
    })
    
    results_path = os.path.join(data_dir, "prediction_results.csv")
    results_df.to_csv(results_path, index=False)
    print(f"预测结果数据已保存至：{results_path}")
    
    return {
        'rmse': rmse,
        'mae': mae,
        'mape': mape,
        'model_path': model_path,
        'results_path': results_path,
        'plot_path': plot_path if save_plot else None
    }

def main(input_filename="flow-kehuo-adjusted.xlsx", 
        output_model="saturation_model.h5",
        train_size=200, 
        time_steps=5, 
        input_dims=6, 
        lstm_units=64,
        epochs=100,
        batch_size=64,
        save_plot=True):
    """主函数"""
    return predict_saturation(
        input_filename=input_filename,
        output_model=output_model,
        train_size=train_size,
        time_steps=time_steps,
        input_dims=input_dims,
        lstm_units=lstm_units,
        epochs=epochs,
        batch_size=batch_size,
        save_plot=save_plot
    )

if __name__ == "__main__":
    main(epochs=10)  # 演示时减少迭代次数