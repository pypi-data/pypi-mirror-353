#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @author :yinzhengjie
# blog:https://www.cnblogs.com/yinzhengjie

from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "服务区饱和度分析系统 - 一个用于分析高速公路服务区饱和度的Python工具包，支持流量分析、饱和度计算和预测功能"

setup(
    # 项目名称
    name='saturation-analysis',
    # 版本号
    version='1.0.1',
    # 项目描述
    description='服务区饱和度分析系统 - 流量分析、饱和度计算和预测',
    long_description=long_description,
    long_description_content_type="text/markdown",
    # 作者信息
    author='服务区饱和度分析系统开发团队',
    author_email='dev@example.com',
    # 项目主页
    # 包含所有发现的包
    packages=find_packages(),
    # 包含非Python文件
    include_package_data=True,
    # 项目依赖
    install_requires=[
        'numpy>=1.19.0',
        'pandas>=1.1.0',
        'matplotlib>=3.3.0',
        'scikit-learn>=0.23.0',
        'tensorflow>=2.3.0',
        'keras>=2.4.0',
        'scikit-fuzzy>=0.4.2',
        'scipy>=1.5.0',
        'scikit-opt>=0.6.0',  # 用于模拟退火算法
        'seaborn>=0.11.0',
        'packaging>=20.0',     # 用于版本比较
        'openpyxl>=3.0.0',     # 用于Excel文件操作
    ],
    # 包含模型文件
    package_data={
        'saturation.pre': ['*.h5'],
    },
    # 分类信息
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    # Python版本要求
    python_requires='>=3.7',
    # 命令行工具
    entry_points={
        "console_scripts": [
            "saturation=saturation.main:main",
        ],
    },
    # 关键词
    keywords="saturation, analysis, traffic, highway, service area",
)
