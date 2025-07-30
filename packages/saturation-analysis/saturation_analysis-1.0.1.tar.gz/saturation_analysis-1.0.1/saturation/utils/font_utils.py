#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
字体工具函数模块 - 提供字体相关配置功能
"""
import os
import sys
import matplotlib.pyplot as plt
import matplotlib as mpl
import platform

def configure_matplotlib_chinese():
    """配置matplotlib以支持中文显示"""
    system = platform.system()
    
    if system == 'Windows':
        # Windows系统优先尝试微软雅黑和黑体
        font_list = ['Microsoft YaHei', 'SimHei', 'SimSun', 'Arial Unicode MS']
    elif system == 'Darwin':  # macOS
        font_list = ['Heiti SC', 'Songti SC', 'STHeiti', 'Arial Unicode MS']
    else:  # Linux等其他系统
        font_list = ['WenQuanYi Micro Hei', 'Droid Sans Fallback', 'Noto Sans CJK SC', 'Arial Unicode MS']
    
    # 尝试设置字体
    font_found = False
    for font_name in font_list:
        try:
            plt.rcParams['font.family'] = font_name
            plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
            # 测试字体是否可用
            mpl.font_manager.findfont(mpl.font_manager.FontProperties(family=font_name))
            print(f"已设置matplotlib中文字体: {font_name}")
            font_found = True
            break
        except Exception:
            continue
    
    if not font_found:
        print("警告: 未找到适合的中文字体，图表中的中文可能无法正确显示")
        # 尝试使用默认的sans-serif字体系列
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS'] + plt.rcParams['font.sans-serif'] 