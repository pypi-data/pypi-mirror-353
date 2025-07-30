#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd

# 定义文件路径
cluster_path = r"E:\魏铨\实验结果\etc\下行\聚类结果_1.csv"
speed_path = r"E:\魏铨\实验结果\etc\下行\速度判别数据_1.csv"
output_path = r"E:\魏铨\实验结果\etc\下行\分类判别_1.csv"

# 读取数据
cluster_data = pd.read_csv(cluster_path)
speed_data = pd.read_csv(speed_path)

# 检查并创建flag列（如果不存在）
if 'flag' not in speed_data.columns:
    speed_data['flag'] = None

# 合并数据集
merged_data = pd.merge(speed_data, cluster_data[['vehicleid', 'passtime_x', 'label']], 
                       on=['vehicleid', 'passtime_x'], how='left')

# 更新flag列
merged_data['flag'] = merged_data.apply(lambda row: row['label'] if pd.notnull(row['label']) else row['flag'], axis=1)

# 选择需要的列
final_data = merged_data[['vehicleid', 'passtime_x', 'vehicletype_x', 'flag']]

# 保存结果
final_data.to_csv(output_path, index=False)
print("数据分类判别完成，结果已保存！")

