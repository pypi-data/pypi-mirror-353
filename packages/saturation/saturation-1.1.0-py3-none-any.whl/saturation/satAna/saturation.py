#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务区饱和度分析系统 - 饱和度分析模块
"""

import pandas as pd
import numpy as np
import os
import pathlib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def get_data_dir():
    """获取数据目录的绝对路径"""
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent.absolute()
    # 向上两级获取项目根目录
    project_root = current_dir.parent.parent
    # 数据目录
    data_dir = os.path.join(project_root, "result")
    return data_dir

def pca_weight(df, column_x, column_y):
    """使用PCA计算权重"""
    # 数据标准化
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df[[column_x, column_y]])
    
    # 应用PCA
    pca = PCA(n_components=2)
    principalComponents = pca.fit_transform(df_scaled)
    
    # 计算每个主成分的方差解释率
    explained_variance = pca.explained_variance_ratio_
    
    # 计算权重（方差解释率）
    weight = explained_variance
    return weight

def analyze_saturation(ke_flow_filename="ke_flow1.csv", huo_flow_filename="huo_flow1.csv",
                      output_filename="merged_flow_saturation_PCA.csv"):
    """进行饱和度分析"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    ke_flow_path = os.path.join(data_dir, ke_flow_filename)
    huo_flow_path = os.path.join(data_dir, huo_flow_filename)
    output_path = os.path.join(data_dir, output_filename)
    
    try:
        # 读取数据
        ke_flow = pd.read_csv(ke_flow_path)
        huo_flow = pd.read_csv(huo_flow_path)
    except FileNotFoundError as e:
        print(f"错误：找不到流量文件 - {e}")
        return None
    
    try:
        # 确保两个文件都有'passtime'列
        if 'passtime' not in ke_flow.columns or 'passtime' not in huo_flow.columns:
            # 检查是否有类似'passtime_x'的列
            for col in ke_flow.columns:
                if 'passtime' in col.lower():
                    ke_flow.rename(columns={col: 'passtime'}, inplace=True)
                    break
            for col in huo_flow.columns:
                if 'passtime' in col.lower():
                    huo_flow.rename(columns={col: 'passtime'}, inplace=True)
                    break
        
        # 合并两个DataFrame
        merged_flow = pd.merge(ke_flow, huo_flow, on='passtime')
        
        # 确定通行能力为实际流量的最大值
        count_x_col = [col for col in merged_flow.columns if col.startswith('inner_ke') or col == 'count_x'][0]
        count_y_col = [col for col in merged_flow.columns if col.startswith('inner_huo') or col == 'count_y'][0]
        
        ke_max_flow = merged_flow[count_x_col].max()
        huo_max_flow = merged_flow[count_y_col].max()
        
        # 确保最大流量不为0，避免除以0
        if ke_max_flow == 0:
            ke_max_flow = 1
        if huo_max_flow == 0:
            huo_max_flow = 1
        
        # 计算流量饱和度
        merged_flow['saturation_ke'] = merged_flow[count_x_col] / ke_max_flow
        merged_flow['saturation_huo'] = merged_flow[count_y_col] / huo_max_flow
        
        # 使用PCA计算权重
        weights = pca_weight(merged_flow, count_x_col, count_y_col)
        print(f"PCA权重: {weights}")

        # 归一化权重，使得权重和为1
        total_weight = weights.sum()
        ke_weight = weights[0] / total_weight
        huo_weight = weights[1] / total_weight
        
        print(f"归一化后的权重 - 客车: {ke_weight:.4f}, 货车: {huo_weight:.4f}")

        # 计算加权后的流量饱和度
        merged_flow['saturation'] = merged_flow['saturation_ke'] * ke_weight + merged_flow['saturation_huo'] * huo_weight

        # 将结果保存至csv文件中
        merged_flow.to_csv(output_path, index=False)
        print(f"饱和度分析结果已保存到：{output_path}")
        return output_path
    except Exception as e:
        print(f"饱和度分析过程中出错：{e}")
        return None

def cluster_saturation(input_filename="merged_flow_saturation_PCA.csv", 
                      output_filename="saturation_clusters.csv",
                      num_clusters=5,
                      save_plot=True):
    """对饱和度进行聚类"""
    try:
        import skfuzzy as fuzz
    except ImportError:
        print("请安装skfuzzy库：pip install scikit-fuzzy")
        return None
        
    data_dir = get_data_dir()
    input_path = os.path.join(data_dir, input_filename)
    output_path = os.path.join(data_dir, output_filename)
    
    try:
        # 读取数据
        df = pd.read_csv(input_path)

        # 提取 saturation 列的数据
        saturation_data = df['saturation'].values.reshape(-1, 1)  # 确保数据是二维的

        # 进行模糊 C 均值聚类
        cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
            data=saturation_data.T,  # 注意：cmeans 需要数据是 (n_samples, n_features) 格式，所以这里转置
            c=num_clusters,          # 聚类数量
            m=2,                     # 模糊化系数，通常设置为 2
            error=0.005,             # 停止迭代的误差阈值
            maxiter=1000,            # 最大迭代次数
            init=None                # 初始化方法，None 表示使用随机初始化
        )

        # cntr 是聚类中心，u 是隶属度矩阵
        # 注意：u 的形状是 (n_clusters, n_samples)，而我们需要的是 (n_samples, n_clusters)
        u = u.T

        # 将聚类结果保存到 DataFrame 中
        df['cluster'] = np.argmax(u, axis=1)  # 获取每个数据点最可能的聚类标签

        # 保存结果
        df.to_csv(output_path, index=False)
        print(f"聚类结果已保存到：{output_path}")

        # 绘制并保存图表
        if save_plot:
            plt.figure(figsize=(12, 8))
            sns.scatterplot(x=df.index, y=df['saturation'], hue=df['cluster'], 
                           palette='viridis', legend='full', s=100)
            plt.title('服务区饱和度模糊C均值聚类结果')
            plt.xlabel('时间序列')
            plt.ylabel('饱和度')
            plt.grid(True)
            
            plot_path = os.path.join(data_dir, "saturation_clusters.png")
            plt.savefig(plot_path)
            plt.close()
            print(f"聚类图表已保存到：{plot_path}")
            
        return output_path
    except Exception as e:
        print(f"聚类分析过程中出错：{e}")
        return None

def main(ke_flow_filename="ke_flow1.csv", huo_flow_filename="huo_flow1.csv",
         output_filename="merged_flow_saturation_PCA.csv", 
         cluster_output="saturation_clusters.csv", 
         num_clusters=5,
         save_plot=True):
    """主函数"""
    # 1. 进行饱和度分析
    result_path = analyze_saturation(ke_flow_filename, huo_flow_filename, output_filename)
    if result_path:
        print(f"饱和度分析完成，结果保存在：{result_path}")
        
        # 2. 进行聚类分析
        cluster_path = cluster_saturation(output_filename, cluster_output, num_clusters, save_plot)
        if cluster_path:
            print(f"聚类分析完成，结果保存在：{cluster_path}")
            return result_path, cluster_path
        else:
            return result_path
    else:
        print("饱和度分析失败，无法进行聚类")
        return None

if __name__ == "__main__":
    main()

