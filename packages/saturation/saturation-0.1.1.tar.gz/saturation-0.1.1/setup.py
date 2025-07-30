#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @author :yinzhengjie
# blog:https://www.cnblogs.com/yinzhengjie

from setuptools import setup, find_packages

setup(
    # 项目名称
    name='saturation',
    # 版本号
    version='0.1.1',
    # 项目描述
    description='服务区饱和度分析系统',
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
        'pandas',
        'numpy',
        'scikit-learn',
        'matplotlib',
        'tensorflow',
        'keras',
    ],
    # 包含模型文件
    package_data={
        'saturation.pre': ['*.h5'],
    },
    # 分类信息
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    # Python版本要求
    python_requires='>=3.7',
)
