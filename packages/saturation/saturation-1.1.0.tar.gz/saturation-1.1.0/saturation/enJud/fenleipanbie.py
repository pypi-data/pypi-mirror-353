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

def classify_data(cluster_filename="聚类结果.csv", speed_filename="速度判别数据.csv", 
                 output_filename="分类判别.csv"):
    """分类判别处理"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    cluster_path = os.path.join(data_dir, cluster_filename)
    speed_path = os.path.join(data_dir, speed_filename)
    output_path = os.path.join(data_dir, output_filename)

    # 读取数据
    cluster_data = pd.read_csv(cluster_path)
    speed_data = pd.read_csv(speed_path)

    # 检查并创建flag列（如果不存在）
    if 'flag' not in speed_data.columns:
        speed_data['flag'] = None

    # 合并数据集
    merged_data = pd.merge(speed_data, cluster_data[['vehicle_id_md5', 'passtime_x', 'label']],
                        on=['vehicle_id_md5', 'passtime_x'], how='left')

    # 更新flag列
    merged_data['flag'] = merged_data.apply(lambda row: row['label'] if pd.notnull(row['label']) else row['flag'], axis=1)

    # 选择需要的列
    final_data = merged_data[['vehicle_id_md5', 'passtime_x', 'vehicletype_x', 'flag']]

    # 保存结果
    final_data.to_csv(output_path, index=False)
    print("数据分类判别完成，结果已保存！")
    return output_path

def main(cluster_filename="聚类结果.csv", speed_filename="速度判别数据.csv", 
         output_filename="分类判别.csv"):
    """主函数"""
    return classify_data(cluster_filename, speed_filename, output_filename)

if __name__ == "__main__":
    main()

