#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务区饱和度分析流程控制器
此模块用于串联不同的分析模块，形成完整的分析流程
"""

import os
import pathlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 导入各个模块
from saturation.enJud import data_process
from saturation.enJud import panbie
from saturation.enJud import huo_canshu
from saturation.enJud import yuzhi
from saturation.enJud import julei
from saturation.enJud import fenleipanbie
from saturation.flow import main as flow_main
from saturation.satAna.saturation import main as saturation_main

def get_data_dir():
    """获取数据目录的绝对路径"""
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent.absolute()
    # 向上一级获取项目根目录
    project_root = current_dir.parent
    # 数据目录
    data_dir = os.path.join(project_root, "result")
    
    # 如果目录不存在，创建它
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"创建数据目录: {data_dir}")
    
    return data_dir

def run_complete_analysis_pipeline(input_data_file="G006550002000620010.csv"):
    """运行完整的分析流程"""
    data_dir = get_data_dir()
    print(f"数据将保存在: {data_dir}")
    
    # 步骤1: 数据处理
    print("\n==== 步骤1: 数据处理 ====")
    data_process.complete_data_processing_pipeline()
    
    # 步骤2: 货车参数分析
    print("\n==== 步骤2: 货车参数分析 ====")
    truck_params = huo_canshu.main(plot=True)
    
    # 步骤3: 计算最优阈值
    print("\n==== 步骤3: 计算最优阈值 ====")
    mu1, mu2 = truck_params['mu1'], truck_params['mu2']
    sigma1, sigma2 = truck_params['sigma1'], truck_params['sigma2']
    w1, w2 = truck_params['w1'], truck_params['w2']
    threshold = yuzhi.main(mu1, mu2, sigma1, sigma2, w1, w2, save_plot=True)
    
    # 步骤4: 速度判别
    print("\n==== 步骤4: 速度判别 ====")
    speed_file = panbie.main(speed_threshold_1=threshold)
    
    # 步骤5: 聚类分析
    print("\n==== 步骤5: 聚类分析 ====")
    cluster_file = julei.main()
    
    # 步骤6: 分类判别
    print("\n==== 步骤6: 分类判别 ====")
    classify_file = fenleipanbie.main()
    
    # 步骤7: 流量分析
    print("\n==== 步骤7: 流量分析 ====")
    flow_results = flow_main()
    
    # 步骤8: 饱和度分析
    print("\n==== 步骤8: 饱和度分析 ====")
    ke_flow_file = "etc_ke_inner.csv"  # 默认文件名
    huo_flow_file = "etc_huo_inner.csv"  # 默认文件名
    
    if flow_results and "ke_inner_flow" in flow_results and "huo_inner_flow" in flow_results:
        ke_flow_file = os.path.basename(flow_results["ke_inner_flow"])
        huo_flow_file = os.path.basename(flow_results["huo_inner_flow"])
    
    saturation_results = saturation_main(
        ke_flow_filename=ke_flow_file,
        huo_flow_filename=huo_flow_file
    )
    print(f"饱和度分析结果保存在: {saturation_results[0] if isinstance(saturation_results, tuple) else saturation_results}")
    
    print("\n==== 分析流程完成 ====")
    print(f"所有结果文件保存在: {data_dir}")
    
    return {
        "data_dir": data_dir,
        "threshold": threshold,
        "truck_params": truck_params,
        "flow_results": flow_results,
        "saturation_results": saturation_results
    }

if __name__ == "__main__":
    run_complete_analysis_pipeline() 