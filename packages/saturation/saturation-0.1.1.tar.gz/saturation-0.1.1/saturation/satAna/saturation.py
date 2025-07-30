#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# 读取数据
ke_flow = pd.read_csv(r"E:\魏铨\实验结果\etc\下行\ke_flow1.csv")
huo_flow = pd.read_csv(r"E:\魏铨\实验结果\etc\下行\huo_flow1.csv")

# 合并两个DataFrame
merged_flow = pd.merge(ke_flow, huo_flow, on='passtime')

# 确定通行能力为实际流量的最大值
ke_max_flow = merged_flow['count_x'].max()
huo_max_flow = merged_flow['count_y'].max()

# 计算流量饱和度
merged_flow['saturation_ke'] = merged_flow['count_x'] / ke_max_flow
merged_flow['saturation_huo'] = merged_flow['count_y'] / huo_max_flow

# 使用PCA计算权重
def pca_weight(df, column_x, column_y):
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

# 计算客车和货车的权重
weights = pca_weight(merged_flow, 'count_x', 'count_y')
print(weights)

# 归一化权重，使得权重和为1
total_weight = weights.sum()
ke_weight = weights[0] / total_weight
huo_weight = weights[1] / total_weight

# 计算加权后的流量饱和度
merged_flow['saturation'] = merged_flow['saturation_ke'] * ke_weight + merged_flow['saturation_huo'] * huo_weight

# 将结果保存至csv文件中
merged_flow.to_csv(r"E:\魏铨\实验结果\etc\下行\merged_flow_saturation_PCA.csv", index=False)


# In[21]:


import pandas as pd
import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt
import seaborn as sns

# 读取数据
df = pd.read_csv(r"E:\魏铨\实验结果\etc\下行\merged_flow_saturation_PCA.csv")

# 提取 saturation 列的数据
saturation_data = df['saturation'].values.reshape(-1, 1)  # 确保数据是二维的

# 设置聚类数量
num_clusters = 5  # 你可以根据需要调整这个值

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

# 如果需要，可以将 df 保存到新的 CSV 文件中
# df.to_csv(r"E:\魏铨\实验结果\etc\下行\merged_flow_saturation_PCA_with_clusters.csv", index=False)

# 绘图
plt.figure(figsize=(10, 6))
sns.scatterplot(x=df.index, y=df['saturation'], hue=df['cluster'], palette='viridis', legend='full', s=100)
plt.title('Fuzzy C-Means Clustering of Saturation Data')
plt.xlabel('Index')
plt.ylabel('Saturation')
plt.show()

