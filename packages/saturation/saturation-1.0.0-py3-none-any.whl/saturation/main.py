#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
服务区饱和度分析系统主程序
"""
import argparse
import os
import pathlib
import time

from saturation.enJud import data_process
from saturation.enJud import julei
from saturation.enJud import fenleipanbie
from saturation.enJud import panbie
from saturation.enJud import yuzhi
from saturation.enJud import huo_canshu
from saturation.satAna import saturation
from saturation.pre import 预测模型 as prediction_model
from saturation import flow

def get_data_dir():
    """获取数据目录的绝对路径"""
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent.absolute()
    # 项目根目录
    project_root = current_dir.parent
    # 数据目录
    data_dir = os.path.join(project_root, "result")
    return data_dir

def process_data():
    """数据处理流程"""
    print("="*50)
    print("开始数据处理...")
    start_time = time.time()
    data_process.complete_data_processing_pipeline()
    end_time = time.time()
    print(f"数据处理完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    
def cluster_analysis():
    """聚类分析"""
    print("="*50)
    print("开始聚类分析...")
    start_time = time.time()
    julei_result = julei.main()
    end_time = time.time()
    print(f"聚类分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return julei_result

def truck_parameter_analysis():
    """货车参数分析"""
    print("="*50)
    print("开始货车参数分析...")
    start_time = time.time()
    result = huo_canshu.main()
    end_time = time.time()
    print(f"货车参数分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result
    
def threshold_analysis():
    """阈值分析"""
    print("="*50)
    print("开始阈值分析...")
    start_time = time.time()
    result = yuzhi.main()
    end_time = time.time()
    print(f"阈值分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result

def speed_classification():
    """速度判别分析"""
    print("="*50)
    print("开始速度判别分析...")
    start_time = time.time()
    result = panbie.main()
    end_time = time.time()
    print(f"速度判别分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result
    
def classification_analysis():
    """分类判别分析"""
    print("="*50)
    print("开始分类判别分析...")
    start_time = time.time()
    result = fenleipanbie.main()
    end_time = time.time()
    print(f"分类判别分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result

def flow_analysis():
    """流量分析"""
    print("="*50)
    print("开始流量分析...")
    start_time = time.time()
    result = flow.main()
    end_time = time.time()
    print(f"流量分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result
    
def saturation_analysis():
    """饱和度分析"""
    print("="*50)
    print("开始饱和度分析...")
    start_time = time.time()
    result = saturation.main()
    end_time = time.time()
    print(f"饱和度分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result
    
def predict():
    """预测饱和度"""
    print("="*50)
    print("开始预测...")
    start_time = time.time()
    result = prediction_model.main()
    end_time = time.time()
    print(f"预测完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result
    
def full_pipeline():
    """执行完整分析流程"""
    print("\n" + "="*60)
    print("开始执行服务区饱和度分析完整流程...")
    print("="*60)
    
    total_start_time = time.time()
    
    # 1. 数据处理
    process_data()
    
    # 2. 聚类分析
    cluster_result = cluster_analysis()
    
    # 3. 货车参数分析
    truck_params = truck_parameter_analysis()
    
    # 4. 阈值分析
    threshold = threshold_analysis()
    
    # 5. 速度判别
    speed_result = speed_classification()
    
    # 6. 分类判别分析
    classification_result = classification_analysis()
    
    # 7. 流量分析
    flow_result = flow_analysis()
    
    # 8. 饱和度分析
    saturation_result = saturation_analysis()
    
    # 9. 饱和度预测
    prediction_result = predict()
    
    total_end_time = time.time()
    print("\n" + "="*60)
    print(f"服务区饱和度分析完整流程执行完毕，总耗时：{total_end_time - total_start_time:.2f}秒")
    print("="*60 + "\n")
    
    return {
        "cluster_result": cluster_result,
        "truck_params": truck_params,
        "threshold": threshold,
        "speed_result": speed_result,
        "classification_result": classification_result,
        "flow_result": flow_result,
        "saturation_result": saturation_result,
        "prediction_result": prediction_result
    }

def main():
    """主程序流程"""
    parser = argparse.ArgumentParser(description='服务区饱和度分析系统')
    parser.add_argument('--process', action='store_true', help='执行数据处理')
    parser.add_argument('--cluster', action='store_true', help='执行聚类分析')
    parser.add_argument('--truck', action='store_true', help='执行货车参数分析')
    parser.add_argument('--threshold', action='store_true', help='执行阈值分析')
    parser.add_argument('--speed', action='store_true', help='执行速度判别')
    parser.add_argument('--classify', action='store_true', help='执行分类判别分析')
    parser.add_argument('--flow', action='store_true', help='执行流量分析')
    parser.add_argument('--analyze', action='store_true', help='执行饱和度分析')
    parser.add_argument('--predict', action='store_true', help='执行预测')
    parser.add_argument('--all', action='store_true', help='执行完整流程')
    
    args = parser.parse_args()
    
    if args.all:
        full_pipeline()
    else:
        if args.process:
            process_data()
        if args.cluster:
            cluster_analysis()
        if args.truck:
            truck_parameter_analysis()
        if args.threshold:
            threshold_analysis()
        if args.speed:
            speed_classification()
        if args.classify:
            classification_analysis()
        if args.flow:
            flow_analysis()
        if args.analyze:
            saturation_analysis()
        if args.predict:
            predict()
            
    print("所有任务完成")

if __name__ == "__main__":
    main() 