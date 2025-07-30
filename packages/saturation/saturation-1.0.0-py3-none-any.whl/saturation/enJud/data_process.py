#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
import pathlib

def get_data_dir():
    """获取数据目录的绝对路径"""
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent.absolute()
    # 向上两级获取项目根目录
    project_root = current_dir.parent.parent
    # 数据目录
    data_dir = os.path.join(project_root, "result")
    return data_dir

def process_initial_data(input_filename="G006550002000620010.csv", output_filename="down.csv"):
    """处理初始数据，去重"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    file_path = os.path.join(data_dir, input_filename)
    
    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 剔除相同vehicle_id_md5和passtime的数据
    # 使用drop_duplicates方法，subset参数指定要比较的列
    df_unique = df.drop_duplicates(subset=['vehicle_id_md5', 'entime'])
    
    # 将去重后的DataFrame写入新的CSV文件
    output_file_path = os.path.join(data_dir, output_filename)
    df_unique.to_csv(output_file_path, index=False)
    
    print(f"去重后的数据已写入到文件：{output_file_path}")
    return output_file_path

def match_vehicles(up_filename="current_up.csv", down_filename="current_down.csv", 
                  output_filename="matched_vehicle_current.csv"):
    """匹配上下行车辆"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    file_path_up = os.path.join(data_dir, up_filename)
    file_path_down = os.path.join(data_dir, down_filename)
    output_file_path = os.path.join(data_dir, output_filename)
    
    # 读取CSV文件
    df_current_up = pd.read_csv(file_path_up)
    df_current_down = pd.read_csv(file_path_down)
    
    # 将'passtime'列转换为pandas的datetime类型
    df_current_up['passtime'] = pd.to_datetime(df_current_up['passtime'])
    df_current_down['passtime'] = pd.to_datetime(df_current_down['passtime'])
    
    # 使用merge函数找出匹配的行
    matched_df = pd.merge(df_current_up, df_current_down, on='vehicle_id_md5', how='inner')
    
    # 计算时间差
    matched_df['time_diff'] = matched_df['passtime_x'] - matched_df['passtime_y']
    
    # 过滤出time_diff大于0的记录
    positive_time_diff_df = matched_df[matched_df['time_diff'] > pd.Timedelta(0)]
    # 过滤时间差小于24小时的数据
    filtered_df = positive_time_diff_df[positive_time_diff_df['time_diff'] < pd.Timedelta(hours=24)]
    
    # 对于每个vehicle_id_md5和passtime_x的组合，找出time_diff最小的行的索引
    idx_min_time_diff = filtered_df.groupby(['vehicle_id_md5', 'passtime_x'])['time_diff'].idxmin()
    
    # 使用这些索引来选择并保留对应的行
    final_df = filtered_df.loc[idx_min_time_diff]
    
    # 将最终的DataFrame写入新的CSV文件
    final_df.to_csv(output_file_path, index=False)
    
    print(f"最终过滤后的数据已写入到文件：{output_file_path}")
    return output_file_path

def filter_matching_entime(filename="matched_vehicle_current.csv"):
    """筛选出entime_x等于entime_y的行"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    file_path = os.path.join(data_dir, filename)
    
    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 筛选出entime_x等于entime_y的行
    filtered_df = df[df['entime_x'] == df['entime_y']]
    
    # 将筛选后的数据保存到新的CSV文件
    filtered_df.to_csv(file_path, index=False)
    return file_path

def calculate_speed(input_filename="matched_vehicle_up.csv", output_filename="speed_up.csv", distance=7.85):
    """计算速度"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    file_path = os.path.join(data_dir, input_filename)
    
    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 确保passtime_x和passtime_y是datetime类型
    df['passtime_x'] = pd.to_datetime(df['passtime_x'])
    df['passtime_y'] = pd.to_datetime(df['passtime_y'])
    
    # 计算时间差（结果为Timedelta类型）
    df['time_diff'] = df['passtime_x'] - df['passtime_y']
    
    # 将时间差转换为小时
    df['time_diff_hours'] = df['time_diff'].dt.total_seconds() / 3600
    
    # 避免除以零的情况，确保时间差不为零
    df = df[df['time_diff_hours'] != 0]
    
    # 计算平均速度v_b
    speed_column = 'v_a'  # 根据输出文件名决定速度列名
    if 'up' in output_filename:
        speed_column = 'v_a'
    elif 'current' in output_filename:
        speed_column = 'v_b'
    elif 'down' in output_filename:
        speed_column = 'v_c'
        
    df[speed_column] = distance / df['time_diff_hours']
    
    # 选择需要保存的字段
    selected_columns = ['vehicle_id_md5', 'passtime_x','passtime_y','entime_x','vehicletype_x', speed_column]
    result_df = df[selected_columns]
    
    # 将结果保存到新的CSV文件
    output_file_path = os.path.join(data_dir, output_filename)
    result_df.to_csv(output_file_path, index=False)
    
    print(f"Selected data with calculated speed has been written to {output_file_path}")
    return output_file_path

def split_by_vehicle_type(input_filename="speed_current.csv", base_output_name="current"):
    """按车辆类型分割数据"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    input_file_path = os.path.join(data_dir, input_filename)
    
    # 读取CSV文件
    df = pd.read_csv(input_file_path)
    
    # 定义保存的文件名
    output_file_0 = os.path.join(data_dir, f"0_{base_output_name}.csv")
    output_file_ke = os.path.join(data_dir, f"ke_{base_output_name}.csv")
    output_file_huo = os.path.join(data_dir, f"huo_{base_output_name}.csv")
    output_file_zuoye = os.path.join(data_dir, f"zuoye_{base_output_name}.csv")
    
    # 根据vehicletype_x的值分割数据
    df_0 = df[df['vehicletype_x'] == 0]
    df_ke = df[(df['vehicletype_x'].isin([1, 2, 3, 4]))]
    df_huo = df[(df['vehicletype_x'].isin([11, 12, 13, 14, 15, 16]))]
    df_zuoye = df[(df['vehicletype_x'].isin([21, 22, 23, 24, 25, 26]))]
    
    # 将分割后的数据分别保存到不同的CSV文件中
    df_0.to_csv(output_file_0, index=False)
    df_ke.to_csv(output_file_ke, index=False)
    df_huo.to_csv(output_file_huo, index=False)
    df_zuoye.to_csv(output_file_zuoye, index=False)
    
    print(f"Data with vehicletype_x == 0 has been written to {output_file_0}")
    print(f"Data with vehicletype_x in [1, 2, 3, 4] has been written to {output_file_ke}")
    print(f"Data with vehicletype_x in [11, 12, 13, 14, 15, 16] has been written to {output_file_huo}")
    print(f"Data with vehicletype_x in [21, 22, 23, 24, 25, 26] has been written to {output_file_zuoye}")
    return {
        'type_0': output_file_0,
        'type_ke': output_file_ke,
        'type_huo': output_file_huo,
        'type_zuoye': output_file_zuoye
    }

def modify_vehicle_types(input_filename="speed_current.csv", output_filename="speed_current1.csv"):
    """修改车辆类型值"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    file_path = os.path.join(data_dir, input_filename)
    file_path1 = os.path.join(data_dir, output_filename)
    
    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 剔除特定 vehicletype_x 的数据
    df = df[~df['vehicletype_x'].isin([0, 21, 22, 23, 24, 25, 26])]
    
    # 修改 vehicletype_x 的值
    df.loc[df['vehicletype_x'].isin([1, 2, 3, 4]), 'vehicletype_x'] = 0
    df.loc[df['vehicletype_x'].isin([11, 12, 13, 14, 15, 16]), 'vehicletype_x'] = 1
    
    # 将修改后的DataFrame保存回CSV文件
    df.to_csv(file_path1, index=False)
    
    print(f"数据已更新并保存到文件：{file_path1}")
    return file_path1

def merge_speed_data(down_filename="speed_down.csv", current_filename="speed_current.csv", 
                   up_filename="speed_up.csv", output_filename="total.csv"):
    """合并速度数据"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    file_path_down = os.path.join(data_dir, down_filename)
    file_path_current = os.path.join(data_dir, current_filename)
    file_path_up = os.path.join(data_dir, up_filename)
    output_file_path = os.path.join(data_dir, output_filename)
    
    # 读取CSV文件
    df_down = pd.read_csv(file_path_down)
    df_current = pd.read_csv(file_path_current)
    df_up = pd.read_csv(file_path_up)
    
    # 将'passtime_x'列转换为pandas的datetime类型
    for df in [df_down, df_current, df_up]:
        df['passtime_x'] = pd.to_datetime(df['passtime_x'])
    
    # 基于vehicle_id_md5合并三个DataFrame
    df_merged = pd.merge(df_down, df_current, on='vehicle_id_md5', how='inner', suffixes=('', '_current'))
    df_merged = pd.merge(df_merged, df_up, on='vehicle_id_md5', how='inner', suffixes=('', '_up'))
    
    # 计算时间差
    df_merged['time_diff_up'] = df_merged['passtime_x_up'] - df_merged['passtime_x_current']
    df_merged['time_diff_down'] = df_merged['passtime_x_current'] - df_merged['passtime_x']
    df_merged['time_diff'] = df_merged['passtime_x_up'] - df_merged['passtime_x']
    
    # 过滤出time_diff_up和time_diff_down都大于0并且小于24小时的记录
    filtered_df = df_merged[(df_merged['time_diff_up'] > pd.Timedelta(0)) & 
                           (df_merged['time_diff_up'] < pd.Timedelta(hours=24)) &
                           (df_merged['time_diff_down'] > pd.Timedelta(0)) & 
                           (df_merged['time_diff_down'] < pd.Timedelta(hours=24))&
                           (df_merged['time_diff'] > pd.Timedelta(0)) & 
                           (df_merged['time_diff'] < pd.Timedelta(hours=24))]
    
    # 对于每个vehicle_id_md5，找出time_diff_down最小的行
    idx_min_time_diff_down = filtered_df.groupby('vehicle_id_md5')['time_diff_down'].idxmin()
    
    # 使用找到的索引来选择对应的行
    min_time_diff_down_rows = filtered_df.loc[idx_min_time_diff_down]
    
    # 在这些行中，找出time_diff_up最小的行
    idx_min_time_diff_up = min_time_diff_down_rows.groupby('vehicle_id_md5')['time_diff_up'].idxmin()
    
    # 使用这些索引来选择并保留对应的行
    final_df = min_time_diff_down_rows.loc[idx_min_time_diff_up]
    
    # 筛选entime_x等于entime_y的行
    final_df1 = final_df[final_df['entime_x'] == final_df['entime_x_current']]
    final_df2 = final_df1[final_df1['entime_x'] == final_df1['entime_x_up']]
    
    # 选择需要的列
    selected_columns = ['vehicle_id_md5','passtime_y' ,'passtime_x', 'passtime_x_current', 'passtime_x_up', 'v_a', 'v_b', 'v_c','vehicletype_x']
    df_final = final_df2[selected_columns]
    
    # 确保选择的列存在
    df_final = df_final[df_final.columns.intersection(selected_columns)]
    
    # 将最终的DataFrame写入新的CSV文件
    df_final.to_csv(output_file_path, index=False)
    
    print(f"符合条件的数据已写入到文件：{output_file_path}")
    return output_file_path

def calculate_p_values(filename="total.csv"):
    """计算p1和p2值"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    file_path = os.path.join(data_dir, filename)
    
    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 确保v_a, v_b, v_c列存在，并且没有空值
    if 'v_a' in df.columns and 'v_b' in df.columns and 'v_c' in df.columns:
        # 计算p1和p2，这里我们假设所有的速度列都是数值类型并且v_a和v_c都不为0
        df['p1'] = df['v_b'] / df['v_a']
        df['p2'] = df['v_b'] / df['v_c']
        
        # 将计算结果保存回CSV文件
        df.to_csv(file_path, index=False)
        print(f"p1和p2已计算并保存到文件：{file_path}")
        return file_path
    else:
        print("CSV文件中缺少必要的列（v_a, v_b, v_c）")
        return None

def filter_vehicle_types_and_p_values(input_filename="total.csv", output_filename="total1.csv", p_threshold=10):
    """过滤车辆类型并限制p值范围"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    file_path = os.path.join(data_dir, input_filename)
    file_path1 = os.path.join(data_dir, output_filename)
    
    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 剔除特定 vehicletype_x 的数据
    df = df[~df['vehicletype_x'].isin([0, 21, 22, 23, 24, 25, 26])]
    
    # 修改 vehicletype_x 的值
    df.loc[df['vehicletype_x'].isin([1, 2, 3, 4]), 'vehicletype_x'] = 0
    df.loc[df['vehicletype_x'].isin([11, 12, 13, 14, 15, 16]), 'vehicletype_x'] = 1
    
    # 筛选p1列小于等于p_threshold且P2列小于等于p_threshold的行
    filtered_df = df[(df['p1'] <= p_threshold) & (df['p2'] <= p_threshold)]
    
    # 将修改后的DataFrame保存回CSV文件
    filtered_df.to_csv(file_path1, index=False)
    
    print(f"数据已更新并保存到文件：{file_path1}")
    return file_path1

def filter_p_values(input_filename="total1.csv", output_filename="total2.csv", p_threshold=2):
    """进一步限制p值范围"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    file_path = os.path.join(data_dir, input_filename)
    file_path1 = os.path.join(data_dir, output_filename)
    
    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 筛选p1列小于等于p_threshold且P2列小于等于p_threshold的行
    filtered_df = df[(df['p1'] <= p_threshold) & (df['p2'] <= p_threshold)]
    
    # 将修改后的DataFrame保存回CSV文件
    filtered_df.to_csv(file_path1, index=False)
    
    print(f"数据已更新并保存到文件：{file_path1}")
    return file_path1

def complete_data_processing_pipeline():
    """执行完整的数据处理流程"""
    # 1. 处理初始数据
    process_initial_data()
    
    # 2. 匹配车辆
    match_vehicles()
    
    # 3. 筛选匹配的entime
    filter_matching_entime()
    
    # 4. 计算各段速度
    calculate_speed(input_filename="matched_vehicle_up.csv", output_filename="speed_up.csv", distance=7.85)
    calculate_speed(input_filename="matched_vehicle_current.csv", output_filename="speed_current.csv", distance=13.15)
    calculate_speed(input_filename="matched_vehicle_down.csv", output_filename="speed_down.csv", distance=12.81)
    
    # 5. 按车辆类型分割数据
    split_by_vehicle_type()
    
    # 6. 修改车辆类型值
    modify_vehicle_types()
    
    # 7. 合并速度数据
    merge_speed_data()
    
    # 8. 计算p值
    calculate_p_values()
    
    # 9. 过滤车辆类型和限制p值范围
    filter_vehicle_types_and_p_values()
    
    # 10. 进一步限制p值范围
    filter_p_values()
    
    print("数据处理流程完成")

if __name__ == "__main__":
    complete_data_processing_pipeline()

