#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @author :yinzhengjie
# blog:https://www.cnblogs.com/yinzhengjie

from setuptools import setup, find_packages
import os

# 读取README文件作为长描述
with open('readme.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    # 项目名称
    name='saturation',
    # 版本号
    version='1.0.0',
    # 项目描述
    description='服务区饱和度分析系统',
    # 长描述
    long_description=long_description,
    long_description_content_type='text/markdown',
    # 作者信息
    author='应用团队',
    # 项目主页
    url='',
    # 包含所有发现的包
    packages=find_packages(),
    # 包含非Python文件
    include_package_data=True,
    # 项目依赖
    install_requires=[
        'pandas>=1.0.0',
        'numpy>=1.18.0',
        'scikit-learn>=0.22.0',
        'matplotlib>=3.1.0',
        'tensorflow>=2.0.0',
        'keras>=2.3.0',
        'scipy>=1.4.0',
        'scikit-fuzzy>=0.4.2',
        'packaging>=20.0',
        'scikit-opt>=0.6.0',  # 用于模拟退火算法
    ],
    # 包含模型文件和数据文件
    package_data={
        'saturation.pre': ['*.h5'],
        'saturation': ['*.csv', '*.xlsx'],
    },
    # 命令行入口点
    entry_points={
        'console_scripts': [
            'saturation-analyze=saturation.main:main',
            'saturation-predict=saturation.pre.预测模型:main',
            'saturation-flow=saturation.flow:main',
        ],
    },
    # 分类信息
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    # Python版本要求
    python_requires='>=3.7',
    # 项目关键字
    keywords='traffic analysis, saturation, prediction, machine learning',
)
