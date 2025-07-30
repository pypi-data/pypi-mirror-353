#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
货车参数分析模块
"""

import os
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import datetime
from scipy.stats import truncnorm
from sklearn.cluster import MiniBatchKMeans, KMeans

def get_data_dir():
    """获取数据目录的绝对路径"""
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent.absolute()
    # 向上两级获取项目根目录
    project_root = current_dir.parent.parent
    # 数据目录
    data_dir = os.path.join(project_root, "result")
    return data_dir

def em_algorithm(h, mu1, sigma1, w1, mu2, sigma2, w2, iterations=60):
    """执行EM算法"""
    d = 1
    n = len(h)  # 样本长度
    
    for _ in range(iterations):
        # E-step - 计算响应
        p1 = w1 * stats.norm(mu1, sigma1).pdf(h)    
        p2 = w2 * stats.truncnorm((0 - mu2) / sigma2, (140 - mu2) / sigma2, mu2, sigma2).pdf(h)
        P = p1 + p2
        R1i = p1 / P
        R2i = p2 / P
      
        # M-step
        # mu1的更新
        mu1 = np.sum(R1i * h) / np.sum(R1i)
           
        # mu2的更新
        m = n * w2 * stats.norm.cdf(-mu2 / sigma2) * (1 - stats.norm.cdf(-mu2 / sigma2))
        x2 = np.sum(R2i * h) / np.sum(R2i)
        s2 = np.sum(R2i * np.square(h - mu2)) / (d * np.sum(R2i))
        u2 = mu2
        mu2 = (1 / (n * w2 + m)) * (n * w2 * x2 + m * (u2 - sigma2 * (stats.norm.pdf(-u2 / sigma2) / stats.norm.cdf(-u2 / sigma2))))
            
        # sigma1的更新
        sigma1 = np.sqrt(np.sum(R1i * np.square(h - mu1)) / (d * np.sum(R1i)))
          
        # sigma2的更新
        sigma2 = np.sqrt((1 / (n * w2 + m)) * (n * w2 * (s2 + (x2 - u2) * (x2 - u2)) + m * sigma2 * sigma2 * (1 - (u2 / sigma2) * (stats.norm.pdf(-u2 / sigma2) / stats.norm.cdf(-u2 / sigma2)))))
        
        # w1的更新
        w1 = np.sum(R1i) / n
        
        # w2的更新
        w2 = np.sum(R2i) / n
    
    return mu1, sigma1, w1, mu2, sigma2, w2

def analyze_truck_parameters(input_filename="speed_current.csv", plot=True, output_plot=None):
    """分析货车参数"""
    data_dir = get_data_dir()
    input_path = os.path.join(data_dir, input_filename)
    
    # 读取CSV文件
    df = pd.read_csv(input_path)
    
    # 筛选vehicletype_x列中值为1, 2, 3, 4的行
    df_ke = df[df['vehicletype_x'].isin([1, 2, 3, 4])]
    # 筛选vehicletype_x列中值为11, 12, 13, 14, 15, 16的行
    df_huo = df[df['vehicletype_x'].isin([11, 12, 13, 14, 15, 16])]
    
    # 获取货车速度数据
    h = df_huo['v_b'].values
    l = len(h)
    X = h.reshape(l, 1)
    
    # 使用K-means聚类
    k_means = KMeans(n_clusters=2, n_init=30) 
    cls = k_means.fit(X) 
    df_huo.index = range(len(df_huo))
    df_huo['lable'] = pd.DataFrame(cls.labels_, columns=['label'])
    df_huo = df_huo[['v_b', 'lable']]
    
    # 分离两个聚类
    df1 = df_huo[df_huo['lable'] == 1]
    df2 = df_huo[df_huo['lable'] == 0]
    df1 = df1[['v_b']]
    df2 = df2[['v_b']]
    
    # GMM的初始化
    mu1 = float(df1.mean())
    sigma1 = float(df1.std())
    w1 = float(len(df1) / len(df_huo)) 
    mu2 = float(df2.mean())
    sigma2 = float(df2.std())
    w2 = float(len(df2) / len(df_huo))
    
    # 执行EM算法
    mu1, sigma1, w1, mu2, sigma2, w2 = em_algorithm(h, mu1, sigma1, w1, mu2, sigma2, w2)
    
    # 输出结果
    results = {
        'mu1': mu1,
        'mu2': mu2,
        'sigma1': sigma1,
        'sigma2': sigma2,
        'w1': w1,
        'w2': w2
    }
    
    print("货车参数分析结果:")
    print(f"分布1: mu={mu1:.2f}, sigma={sigma1:.2f}, weight={w1:.2f}")
    print(f"分布2: mu={mu2:.2f}, sigma={sigma2:.2f}, weight={w2:.2f}")
    
    # 绘制图形
    if plot:
        t = np.linspace(0, 160, 500)
        m = stats.norm.pdf(t, loc=mu1, scale=sigma1)  # 不进入服务区分布的预测
        f = stats.norm.pdf(t, loc=mu2, scale=sigma2)  # 进入服务区分布的预测
        mix = w1 * m + w2 * f  # 混合后
        
        plt.figure(figsize=(10, 6))
        plt.hist(h, bins=100, density=True, alpha=0.5, color='gray')
        plt.plot(t, m, color='b', label='分布1')
        plt.plot(t, f, color='r', label='分布2')
        plt.plot(t, mix, color='k', label='混合分布')
        plt.title('货车速度分布EM混合高斯模型')
        plt.xlabel('速度 (km/h)')
        plt.ylabel('概率密度')
        plt.legend()
        
        if output_plot:
            output_path = os.path.join(data_dir, output_plot)
            plt.savefig(output_path)
            print(f"图形已保存到: {output_path}")
        else:
            plt.show()
    
    return results

def main(input_filename="speed_current.csv", plot=True, output_plot="truck_speed_distribution.png"):
    """主函数"""
    return analyze_truck_parameters(input_filename, plot, output_plot)

if __name__ == "__main__":
    main()