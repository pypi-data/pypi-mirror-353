#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务区饱和度分析系统 - API模块

提供简单、统一的接口访问饱和度分析系统的各个功能。
"""

import os
import pathlib
import pandas as pd
import numpy as np

from .enJud.data_process import complete_data_processing_pipeline, process_initial_data
from .enJud.julei import perform_clustering
from .enJud.fenleipanbie import classify_data
from .enJud.yuzhi import calculate_threshold
from .enJud.huo_canshu import analyze_truck_parameters
from .enJud import panbie
from .flow import create_merged_flow_file, calculate_flow, calculate_inner_outer_flow, calculate_vehicle_type_flow, calculate_time_values, adjust_flow
from .satAna.saturation import analyze_saturation, cluster_saturation
from .pre.预测模型 import predict_saturation

# 通用API

def set_data_dir(data_dir):
    """设置全局数据目录
    
    Args:
        data_dir (str): 数据目录的路径
        
    Returns:
        str: 设置的数据目录路径
    """
    os.environ['SATURATION_DATA_DIR'] = os.path.abspath(data_dir)
    return os.environ['SATURATION_DATA_DIR']

def get_data_dir():
    """获取全局数据目录
    
    如果环境变量中设置了SATURATION_DATA_DIR，则使用该目录
    否则使用项目根目录下的result目录
    
    Returns:
        str: 数据目录路径
    """
    if 'SATURATION_DATA_DIR' in os.environ:
        return os.environ['SATURATION_DATA_DIR']
    
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent.absolute()
    # 项目根目录
    project_root = current_dir.parent
    # 数据目录
    data_dir = os.path.join(project_root, "result")
    
    # 确保目录存在
    os.makedirs(data_dir, exist_ok=True)
    
    return data_dir
    
# 数据处理API

def process_data(input_file=None, output_file=None, data_dir=None):
    """处理原始ETC数据
    
    Args:
        input_file (str, optional): 输入文件名，默认为G006550002000620010.csv
        output_file (str, optional): 输出文件名，默认为down.csv
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        str: 输出文件路径
    """
    if data_dir is None:
        data_dir = get_data_dir()
        
    if input_file is None:
        input_file = "G006550002000620010.csv"
        
    if output_file is None:
        output_file = "down.csv"
    
    return process_initial_data(input_filename=input_file, output_filename=output_file, custom_data_dir=data_dir)
    
def run_complete_data_processing(data_dir=None):
    """执行完整的数据处理管道
    
    Args:
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        bool: 处理成功返回True
    """
    complete_data_processing_pipeline(custom_data_dir=data_dir)
    return True

# 聚类分析API

def cluster_analysis(input_file="total.csv", output_file="聚类结果.csv", 
                    n_components=2, test_size=0.2, plot=False, data_dir=None):
    """执行聚类分析
    
    Args:
        input_file (str, optional): 输入文件名，默认为total.csv
        output_file (str, optional): 输出文件名，默认为聚类结果.csv
        n_components (int, optional): 聚类数量，默认为2
        test_size (float, optional): 测试集比例，默认为0.2
        plot (bool, optional): 是否生成图表，默认为False
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        str: 输出文件路径
    """
    if data_dir is None:
        data_dir = get_data_dir()
        
    return perform_clustering(
        input_filename=input_file,
        output_filename=output_file,
        n_components=n_components,
        test_size=test_size,
        plot=plot,
        custom_data_dir=data_dir
    )
    
# 分类判别API

def classify_speed_data(input_file="speed_current1.csv", output_file="速度判别数据.csv",
                       speed_threshold_0=None, speed_threshold_1=None, data_dir=None):
    """根据速度阈值进行分类判别
    
    Args:
        input_file (str, optional): 输入文件名，默认为speed_current1.csv
        output_file (str, optional): 输出文件名，默认为速度判别数据.csv
        speed_threshold_0 (float, optional): 客车速度阈值，默认为66.268
        speed_threshold_1 (float, optional): 货车速度阈值，默认为39.582
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        str: 输出文件路径
    """
    if data_dir is None:
        data_dir = get_data_dir()
    
    if speed_threshold_0 is None:
        speed_threshold_0 = 66.268
        
    if speed_threshold_1 is None:
        speed_threshold_1 = 39.582
        
    return panbie.classify_by_speed(
        input_filename=input_file,
        output_filename=output_file,
        speed_threshold_0=speed_threshold_0,
        speed_threshold_1=speed_threshold_1,
        custom_data_dir=data_dir
    )
    
def classify_data_by_cluster(cluster_file="聚类结果.csv", speed_file="速度判别数据.csv", 
                           output_file="分类判别.csv", data_dir=None):
    """根据聚类结果进行分类判别
    
    Args:
        cluster_file (str, optional): 聚类结果文件名，默认为聚类结果.csv
        speed_file (str, optional): 速度判别文件名，默认为速度判别数据.csv
        output_file (str, optional): 输出文件名，默认为分类判别.csv
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        str: 输出文件路径
    """
    if data_dir is None:
        data_dir = get_data_dir()
        
    return classify_data(
        cluster_filename=cluster_file,
        speed_filename=speed_file,
        output_filename=output_file,
        custom_data_dir=data_dir
    )
    
# 阈值分析API

def analyze_threshold(mu1=69.24, mu2=15.42, sigma1=10.22, sigma2=9.47, 
                     w1=0.7, w2=0.3, save_plot=True, output_plot="threshold_plot.png", data_dir=None):
    """计算最优阈值
    
    Args:
        mu1 (float, optional): 第一个分布的均值，默认为69.24
        mu2 (float, optional): 第二个分布的均值，默认为15.42
        sigma1 (float, optional): 第一个分布的标准差，默认为10.22
        sigma2 (float, optional): 第二个分布的标准差，默认为9.47
        w1 (float, optional): 第一个分布的权重，默认为0.7
        w2 (float, optional): 第二个分布的权重，默认为0.3
        save_plot (bool, optional): 是否保存图表，默认为True
        output_plot (str, optional): 输出图表文件名，默认为threshold_plot.png
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        float: 计算出的最优阈值
    """
    # 注意：虽然yuzhi.py中没有直接支持自定义输出图表文件名，
    # 但由于数据目录是可以自定义的，可以通过不同数据目录来实现输出文件的区分
    return calculate_threshold(
        mu1=mu1, mu2=mu2, 
        sigma1=sigma1, sigma2=sigma2, 
        w1=w1, w2=w2, 
        save_plot=save_plot,
        custom_data_dir=data_dir
    )
    
# 货车参数分析API

def analyze_truck_params(input_file="speed_current.csv", plot=True, 
                        output_plot="truck_speed_distribution.png", data_dir=None):
    """分析货车参数
    
    Args:
        input_file (str, optional): 输入文件名，默认为speed_current.csv
        plot (bool, optional): 是否生成图表，默认为True
        output_plot (str, optional): 图表输出文件名，默认为truck_speed_distribution.png
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        dict: 包含分析结果的字典
    """
    return analyze_truck_parameters(
        input_filename=input_file,
        plot=plot,
        output_plot=output_plot,
        custom_data_dir=data_dir
    )

# 单独的流量分析功能API

def calculate_time_values_api(input_file="速度判别数据.csv", distance=3.6, data_dir=None):
    """计算时间值API
    
    Args:
        input_file (str, optional): 输入文件名，默认为"速度判别数据.csv"
        distance (float, optional): 距离参数，默认为3.6
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        tuple: 包含客车(t0)和货车(t1)时间值的元组
    """
    if data_dir is None:
        data_dir = get_data_dir()
        
    return calculate_time_values(input_filename=input_file, distance=distance, data_dir=data_dir)

def adjust_flow_api(input_file="分类判别.csv", output_file="flow_adjust.csv", data_dir=None):
    """调整流量API
    
    Args:
        input_file (str, optional): 输入文件名，默认为"分类判别.csv"
        output_file (str, optional): 输出文件名，默认为"flow_adjust.csv"
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        str: 输出文件路径
    """
    if data_dir is None:
        data_dir = get_data_dir()
        
    return adjust_flow(input_filename=input_file, output_filename=output_file, data_dir=data_dir)

def calculate_flow_api(input_file="speed_current1.csv", output_file="etc_flow.csv", data_dir=None):
    """计算流量API
    
    Args:
        input_file (str, optional): 输入文件名，默认为"speed_current1.csv"
        output_file (str, optional): 输出文件名，默认为"etc_flow.csv"
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        str: 输出文件路径
    """
    if data_dir is None:
        data_dir = get_data_dir()
        
    return calculate_flow(input_filename=input_file, output_filename=output_file, data_dir=data_dir)

def calculate_inner_outer_flow_api(input_file="speed_current.csv", 
                                  inner_file="inner.csv", 
                                  outer_file="outer.csv",
                                  data_dir=None):
    """计算内部和外部流量API
    
    Args:
        input_file (str, optional): 输入文件名，默认为"speed_current.csv"
        inner_file (str, optional): 内部流量输出文件名，默认为"inner.csv"
        outer_file (str, optional): 外部流量输出文件名，默认为"outer.csv"
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        tuple: 包含内部和外部流量文件路径的元组
    """
    if data_dir is None:
        data_dir = get_data_dir()
        
    return calculate_inner_outer_flow(
        input_filename=input_file,
        inner_filename=inner_file,
        outer_filename=outer_file,
        data_dir=data_dir
    )

def calculate_vehicle_type_flow_api(input_file="speed_current.csv", 
                                   ke_inner_file="etc_ke_inner.csv", 
                                   ke_outer_file="etc_ke_outer.csv",
                                   huo_inner_file="etc_huo_inner.csv", 
                                   huo_outer_file="etc_huo_outer.csv",
                                   data_dir=None):
    """计算不同车型的内外流量API
    
    Args:
        input_file (str, optional): 输入文件名，默认为"speed_current.csv"
        ke_inner_file (str, optional): 客车内部流量输出文件名，默认为"etc_ke_inner.csv"
        ke_outer_file (str, optional): 客车外部流量输出文件名，默认为"etc_ke_outer.csv"
        huo_inner_file (str, optional): 货车内部流量输出文件名，默认为"etc_huo_inner.csv"
        huo_outer_file (str, optional): 货车外部流量输出文件名，默认为"etc_huo_outer.csv"
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        tuple: 包含客车内外流量和货车内外流量文件路径的元组
    """
    if data_dir is None:
        data_dir = get_data_dir()
        
    return calculate_vehicle_type_flow(
        input_filename=input_file,
        ke_inner_filename=ke_inner_file,
        ke_outer_filename=ke_outer_file,
        huo_inner_filename=huo_inner_file,
        huo_outer_filename=huo_outer_file,
        data_dir=data_dir
    )

# 流量分析API

def analyze_flow(input_file="speed_current1.csv", data_dir=None, output_dir=None, 
               custom_flow_files=None, output_files=None):
    """执行完整的流量分析流程
    
    Args:
        input_file (str, optional): 输入文件名，默认为speed_current1.csv
        data_dir (str, optional): 输入数据目录，默认使用get_data_dir()
        output_dir (str, optional): 输出数据目录，默认与data_dir相同
        custom_flow_files (list, optional): 自定义流量文件列表，用于合并流量文件
        output_files (dict, optional): 自定义输出文件名字典，可包含以下键：
            - flow_adjust: 流量调整文件名，默认为"flow_adjust.csv"
            - etc_flow: ETC流量文件名，默认为"etc_flow.csv"
            - inner_flow: 内部流量文件名，默认为"inner.csv"
            - outer_flow: 外部流量文件名，默认为"outer.csv"
            - ke_inner_flow: 客车内部流量文件名，默认为"etc_ke_inner.csv"
            - ke_outer_flow: 客车外部流量文件名，默认为"etc_ke_outer.csv"
            - huo_inner_flow: 货车内部流量文件名，默认为"etc_huo_inner.csv"
            - huo_outer_flow: 货车外部流量文件名，默认为"etc_huo_outer.csv"
            - merged_flow: 合并流量文件名，默认为"flow-kehuo-adjusted.xlsx"
        
    Returns:
        dict: 包含各步骤结果文件路径的字典
    """
    if data_dir is None:
        data_dir = get_data_dir()
        
    if output_dir is None:
        output_dir = data_dir
        
    # 初始化默认输出文件名
    default_output_files = {
        'flow_adjust': "flow_adjust.csv",
        'etc_flow': "etc_flow.csv",
        'inner_flow': "inner.csv",
        'outer_flow': "outer.csv",
        'ke_inner_flow': "etc_ke_inner.csv",
        'ke_outer_flow': "etc_ke_outer.csv",
        'huo_inner_flow': "etc_huo_inner.csv",
        'huo_outer_flow': "etc_huo_outer.csv",
        'merged_flow': "flow-kehuo-adjusted.xlsx"
    }
    
    # 更新输出文件名（如果提供了）
    if output_files is not None:
        default_output_files.update(output_files)
    
    from .flow import main as flow_main
    return flow_main(
        input_file=input_file,
        data_dir=data_dir,
        output_dir=output_dir,
        custom_flow_files=custom_flow_files,
        output_files=default_output_files
    )
    
def create_flow_file(output_file="flow-kehuo-adjusted.xlsx", data_dir=None, input_files=None):
    """创建用于预测模型的流量文件
    
    Args:
        output_file (str, optional): 输出文件名，默认为flow-kehuo-adjusted.xlsx
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        input_files (list, optional): 自定义输入文件列表，默认为None时使用标准文件列表
        
    Returns:
        str: 输出文件路径
    """
    if data_dir is None:
        data_dir = get_data_dir()
        
    return create_merged_flow_file(
        output_filename=output_file,
        data_dir=data_dir,
        input_files=input_files
    )
    
# 饱和度分析API

def analyze_saturation_data(ke_flow_file="ke_flow1.csv", huo_flow_file="huo_flow1.csv",
                          output_file="merged_flow_saturation_PCA.csv", data_dir=None):
    """进行饱和度分析
    
    Args:
        ke_flow_file (str, optional): 客车流量文件名，默认为ke_flow1.csv
        huo_flow_file (str, optional): 货车流量文件名，默认为huo_flow1.csv
        output_file (str, optional): 输出文件名，默认为merged_flow_saturation_PCA.csv
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        str: 输出文件路径
    """
    return analyze_saturation(
        ke_flow_filename=ke_flow_file,
        huo_flow_filename=huo_flow_file,
        output_filename=output_file,
        custom_data_dir=data_dir
    )
    
def cluster_saturation_data(input_file="merged_flow_saturation_PCA.csv", 
                          output_file="saturation_clusters.csv",
                          num_clusters=5, save_plot=True, plot_file="saturation_clusters.png", data_dir=None):
    """对饱和度进行聚类
    
    Args:
        input_file (str, optional): 输入文件名，默认为merged_flow_saturation_PCA.csv
        output_file (str, optional): 输出文件名，默认为saturation_clusters.csv
        num_clusters (int, optional): 聚类数量，默认为5
        save_plot (bool, optional): 是否保存图表，默认为True
        plot_file (str, optional): 图表输出文件名，默认为saturation_clusters.png
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        str: 输出文件路径
    """
    return cluster_saturation(
        input_filename=input_file,
        output_filename=output_file,
        num_clusters=num_clusters,
        save_plot=save_plot,
        plot_filename=plot_file,
        custom_data_dir=data_dir
    )
    
# 预测API

def predict(input_file="flow-kehuo-adjusted.xlsx", 
           output_model="saturation_model.h5",
           output_results="prediction_results.csv",
           output_plot="saturation_prediction.png",
           train_size=200, 
           time_steps=5, 
           input_dims=6, 
           lstm_units=64,
           epochs=100,
           batch_size=64,
           save_plot=True,
           data_dir=None):
    """预测饱和度
    
    Args:
        input_file (str, optional): 输入文件名，默认为flow-kehuo-adjusted.xlsx
        output_model (str, optional): 模型输出文件名，默认为saturation_model.h5
        output_results (str, optional): 预测结果输出文件名，默认为prediction_results.csv
        output_plot (str, optional): 图表输出文件名，默认为saturation_prediction.png
        train_size (int, optional): 训练集大小，默认为200
        time_steps (int, optional): 时间步长，默认为5
        input_dims (int, optional): 输入维度，默认为6
        lstm_units (int, optional): LSTM单元数，默认为64
        epochs (int, optional): 训练轮数，默认为100
        batch_size (int, optional): 批处理大小，默认为64
        save_plot (bool, optional): 是否保存图表，默认为True
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        
    Returns:
        dict: 包含预测结果的字典
    """
    return predict_saturation(
        input_filename=input_file,
        output_model=output_model,
        output_results=output_results,
        output_plot=output_plot,
        train_size=train_size,
        time_steps=time_steps,
        input_dims=input_dims,
        lstm_units=lstm_units,
        epochs=epochs,
        batch_size=batch_size,
        save_plot=save_plot,
        custom_data_dir=data_dir
    )
    
# 完整分析流程

def run_full_pipeline(data_dir=None, output_dir=None, output_files=None):
    """运行完整的饱和度分析流程
    
    Args:
        data_dir (str, optional): 数据目录，默认使用get_data_dir()
        output_dir (str, optional): 输出目录，默认与data_dir相同
        output_files (dict, optional): 自定义输出文件名字典
        
    Returns:
        dict: 包含完整分析结果的字典
    """
    if data_dir is None:
        data_dir = get_data_dir()
        
    if output_dir is None:
        output_dir = data_dir
    
    from .main import full_pipeline
    return full_pipeline(custom_data_dir=data_dir, output_dir=output_dir, output_files=output_files) 