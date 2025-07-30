#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

# 指定文件路径
file_path = r"E:\魏铨\实验结果\etc\下行\速度判别数据.csv"
L=3.6 #单位km
# 读取CSV文件
df = pd.read_csv(file_path)

# 筛选出flag为0的行
filtered_df = df[df['flag'] == 0]

# 计算vehicletype_x为0时v_b的平均值
mean_vb_type_0 = filtered_df[filtered_df['vehicletype_x'] == 0]['v_b'].mean()

# 计算vehicletype_x为1时v_b的平均值
mean_vb_type_1 = filtered_df[filtered_df['vehicletype_x'] == 1]['v_b'].mean()

# 计算t0和t1，假设v_b单位为km/h，转换为h/km后计算时间
t0 = L / mean_vb_type_0 * 3600  # 将时间转换为秒
t1 = L / mean_vb_type_1 * 3600  # 将时间转换为秒

# 打印结果
print(f"Time t0 for vehicletype_x = 0 when flag = 0: {t0:.2f} seconds")
print(f"Time t1 for vehicletype_x = 1 when flag = 0: {t1:.2f} seconds")


# In[2]:


import pandas as pd

# 指定文件路径
input_file_path = r"E:\魏铨\实验结果\etc\下行\分类判别.csv"
flow_csv = r"E:\魏铨\实验结果\etc\下行\flow_adjust.csv"

# 读取CSV文件
df = pd.read_csv(input_file_path)

# 确保passtime是datetime类型
df['passtime'] = pd.to_datetime(df['passtime'])

# 根据vehicletype_x的值调整passtime_x
time_adjustment_0 = pd.Timedelta(seconds=146.95)
time_adjustment_1 = pd.Timedelta(seconds=192.32)
df.loc[df['vehicletype_x'] == 0, 'passtime'] += time_adjustment_0
df.loc[df['vehicletype_x'] == 1, 'passtime'] += time_adjustment_1

# 使用Grouper来实现每60分钟的分组
flow_etc = df.groupby(pd.Grouper(key='passtime', freq='60min')).size().reset_index(name='flow_etc')

# 筛选出flag为1的行
flagged_df = df[df['flag'] == 1]

# 每半个小时统计etc的数据条数
flow_b = flagged_df.groupby(pd.Grouper(key='passtime', freq='60min')).size().reset_index(name='flow')

# 合并flow_etc和flow_b
flow_merged = pd.merge(flow_etc, flow_b, on='passtime', how='inner')

# 计算flow_b/flow_etc的比值
flow_merged['ratio'] = flow_merged['flow'] / flow_merged['flow_etc']

# 计算均值k
k = flow_merged['ratio'].mean()
print(f"Mean ratio (k): {k}")

# 若flow_b/flow_etc>0.4,则flow_b的值为flow_etc*k，结果取整
flow_merged['flow'] = flow_merged.apply(lambda row: int(row['flow_etc'] * k) if row['ratio'] > 0.4 else row['flow'], axis=1)

# 删除中间计算的ratio列
flow_merged.drop('ratio', axis=1, inplace=True)

# 将统计结果保存到CSV
flow_merged.to_csv(flow_csv, index=False)

print(f"Flow data has been saved to {flow_csv}")


# In[2]:


import pandas as pd

# 指定文件路径
input_file_path = r"E:\魏铨\实验结果\etc\下行\speed_current_1.csv"
output_csv = r"E:\魏铨\实验结果\etc\下行\etc_flow.csv"

# 读取CSV文件
df = pd.read_csv(input_file_path)

# 确保passtime_x是datetime类型
df['passtime_x'] = pd.to_datetime(df['passtime_x'])

# 根据vehicletype_x的值分割数据
df_ke = df[df['vehicletype_x'].isin([1, 2, 3, 4])]
df_huo = df[df['vehicletype_x'].isin([11, 12, 13, 14, 15, 16])]

# 根据vehicletype_x的值调整passtime_x
time_adjustment_ke = pd.Timedelta(seconds=147.21)
time_adjustment_huo = pd.Timedelta(seconds=192.63)
df_ke['passtime_x'] += time_adjustment_ke
df_huo['passtime_x'] += time_adjustment_huo

# 每60分钟统计所有数据条数
etc_flow_count = df.groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='etc_flow')

# 客车每60分钟的数据条数
etc_fke_count = df_ke.groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='etc_fke')

# 货车每60分钟的数据条数
etc_fhuo_count = df_huo.groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='etc_fhuo')

# 合并三个DataFrame
merged_df = pd.merge(etc_flow_count, etc_fke_count, on='passtime_x', how='left')
merged_df = pd.merge(merged_df, etc_fhuo_count, on='passtime_x', how='left')

# 将合并后的数据保存到CSV文件
merged_df.to_csv(output_csv, index=False)

print(f"All flow data has been saved to {output_csv}")


# In[2]:


import pandas as pd
from datetime import datetime

# 读取CSV文件
input_file_path = r"E:\魏铨\实验结果\etc\下行\speed_current.csv"
data = pd.read_csv(input_file_path)

# 定义一个函数来判断是否为重庆市车牌
def is_chongqing_license_plate(vehicleid):
    # 重庆市车牌的前缀
    prefixes = ['渝A', '渝B', '渝C', '渝D', '渝E', '渝F', '渝G', '渝H', '渝I']
    return any(vehicleid.startswith(prefix) for prefix in prefixes)

# 增加一个新列'flag'，根据车牌号判断是否为重庆市车牌
data['flag'] = data['vehicleid'].apply(is_chongqing_license_plate)

# 将时间字符串转换为时间对象
data['passtime_x'] = pd.to_datetime(data['passtime_x'])

# 筛选客运车辆
df_ke = data[data['vehicletype_x'].isin([1, 2, 3, 4])]
# 筛选货运车辆
df_huo = data[data['vehicletype_x'].isin([11, 12, 13, 14, 15, 16])]

# 根据vehicletype_x的值调整passtime_x
time_adjustment_0 = pd.Timedelta(seconds=147.21)
time_adjustment_1 = pd.Timedelta(seconds=192.63)
df_ke['passtime_x'] += time_adjustment_0
df_huo['passtime_x'] += time_adjustment_1

# 定义一个函数来统计每半小时的数据条数
def count_every_half_hour(group):
    return len(group)

# 分组并统计数据
inner = data[data['flag'] == 1].groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='inner')
outer = data[data['flag'] == 0].groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='outer')

# 保存结果到CSV文件
inner.to_csv(r"E:\魏铨\实验结果\etc\下行\inner.csv", index=False)
outer.to_csv(r"E:\魏铨\实验结果\etc\下行\outer.csv", index=False)

print("处理完成，结果已保存。")


# In[1]:


import pandas as pd

# 读取CSV文件
input_file_path = r"E:\魏铨\实验结果\etc\下行\speed_current.csv"
ke_inner = r"E:\魏铨\实验结果\etc\下行\etc_ke_inner_1.csv"
ke_outer = r"E:\魏铨\实验结果\etc\下行\etc_ke_outer_1.csv"
huo_inner = r"E:\魏铨\实验结果\etc\下行\etc_huo_inner_1.csv"
huo_outer = r"E:\魏铨\实验结果\etc\下行\etc_huo_outer_1.csv"
data = pd.read_csv(input_file_path)

# 定义一个函数来判断是否为重庆市车牌
def is_chongqing_license_plate(vehicleid):
    # 重庆市车牌的前缀
    prefixes = ['渝A', '渝B', '渝C', '渝D', '渝E', '渝F', '渝G', '渝H', '渝I']
    return any(vehicleid.startswith(prefix) for prefix in prefixes)

# 增加一个新列'flag'，根据车牌号判断是否为重庆市车牌
data['flag'] = data['vehicleid'].apply(is_chongqing_license_plate)

# 将时间字符串转换为时间对象
data['passtime_x'] = pd.to_datetime(data['passtime_x'])

# 筛选客运车辆
df_ke = data[data['vehicletype_x'].isin([1, 2, 3, 4])]
# 筛选货运车辆
df_huo = data[data['vehicletype_x'].isin([11, 12, 13, 14, 15, 16])]

# 根据vehicletype_x的值调整passtime_x
time_adjustment_0 = pd.Timedelta(seconds=147.21)
time_adjustment_1 = pd.Timedelta(seconds=192.63)
df_ke['passtime_x'] += time_adjustment_0
df_huo['passtime_x'] += time_adjustment_1

# 分别统计客运车辆的市内车流量和市外车流量
inner_ke = df_ke[df_ke['flag']].groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='inner_ke')
outer_ke = df_ke[~df_ke['flag']].groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='outer_ke')

# 分别统计货运车辆的市内车流量和市外车流量
inner_huo = df_huo[df_huo['flag']].groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='inner_huo')
outer_huo = df_huo[~df_huo['flag']].groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='outer_huo')

# 保存结果到CSV文件
inner_ke .to_csv(ke_inner, index=False)
outer_ke.to_csv(ke_outer, index=False)
inner_huo .to_csv(huo_inner, index=False)
outer_huo.to_csv(huo_outer, index=False)

print("处理完成，结果已保存。")

