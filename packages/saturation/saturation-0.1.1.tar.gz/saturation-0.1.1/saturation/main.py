#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
服务区饱和度分析系统主程序
"""
import argparse
import os
import pathlib

from saturation.enJud import data_process
from saturation.enJud import julei
from saturation.satAna import saturation
from saturation.pre import 预测模型 as prediction_model

def get_data_dir():
    """获取数据目录的绝对路径"""
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent.absolute()
    # 项目根目录
    project_root = current_dir.parent
    # 数据目录
    data_dir = os.path.join(project_root, "data")
    return data_dir

def process_data():
    """数据处理流程"""
    print("开始数据处理...")
    data_process.complete_data_processing_pipeline()
    print("数据处理完成")
    
def cluster_analysis():
    """聚类分析"""
    print("开始聚类分析...")
    julei_result = julei.main()
    print(f"聚类分析完成: {julei_result}")
    
def saturation_analysis():
    """饱和度分析"""
    print("开始饱和度分析...")
    result = saturation.main()
    print(f"饱和度分析完成: {result}")
    
def predict():
    """预测饱和度"""
    print("开始预测...")
    result = prediction_model.main()
    print(f"预测完成: {result}")
    
def main():
    """主程序流程"""
    parser = argparse.ArgumentParser(description='服务区饱和度分析系统')
    parser.add_argument('--process', action='store_true', help='执行数据处理')
    parser.add_argument('--cluster', action='store_true', help='执行聚类分析')
    parser.add_argument('--analyze', action='store_true', help='执行饱和度分析')
    parser.add_argument('--predict', action='store_true', help='执行预测')
    parser.add_argument('--all', action='store_true', help='执行完整流程')
    
    args = parser.parse_args()
    
    if args.all:
        process_data()
        cluster_analysis()
        saturation_analysis()
        predict()
    else:
        if args.process:
            process_data()
        if args.cluster:
            cluster_analysis()
        if args.analyze:
            saturation_analysis()
        if args.predict:
            predict()
            
    print("所有任务完成")

if __name__ == "__main__":
    main() 