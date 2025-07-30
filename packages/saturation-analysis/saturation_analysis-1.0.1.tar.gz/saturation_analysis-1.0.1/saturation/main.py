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

def get_data_dir(custom_data_dir=None):
    """获取数据目录的绝对路径
    
    Args:
        custom_data_dir: 自定义数据目录路径，如果提供则直接返回
    """
    # 如果提供了自定义数据目录，直接返回
    if custom_data_dir is not None:
        return custom_data_dir
        
    # 否则使用默认路径
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent.absolute()
    # 项目根目录
    project_root = current_dir.parent
    # 数据目录
    data_dir = os.path.join(project_root, "result")
    return data_dir

def process_data(custom_data_dir=None):
    """数据处理流程"""
    print("="*50)
    print("开始数据处理...")
    start_time = time.time()
    data_process.complete_data_processing_pipeline()
    end_time = time.time()
    print(f"数据处理完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    
def cluster_analysis(custom_data_dir=None, output_file=None):
    """聚类分析"""
    print("="*50)
    print("开始聚类分析...")
    start_time = time.time()
    julei_result = julei.main(custom_data_dir=custom_data_dir, output_filename=output_file)
    end_time = time.time()
    print(f"聚类分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return julei_result

def truck_parameter_analysis(custom_data_dir=None, output_plot=None):
    """货车参数分析"""
    print("="*50)
    print("开始货车参数分析...")
    start_time = time.time()
    result = huo_canshu.main(custom_data_dir=custom_data_dir, output_plot=output_plot)
    end_time = time.time()
    print(f"货车参数分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result
    
def threshold_analysis(custom_data_dir=None, output_plot=None):
    """阈值分析"""
    print("="*50)
    print("开始阈值分析...")
    start_time = time.time()
    result = yuzhi.main(custom_data_dir=custom_data_dir, save_plot=True, output_plot=output_plot)
    end_time = time.time()
    print(f"阈值分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result

def speed_classification(custom_data_dir=None, output_file=None):
    """速度判别分析"""
    print("="*50)
    print("开始速度判别分析...")
    start_time = time.time()
    result = panbie.main(custom_data_dir=custom_data_dir, output_filename=output_file)
    end_time = time.time()
    print(f"速度判别分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result
    
def classification_analysis(custom_data_dir=None, output_file=None):
    """分类判别分析"""
    print("="*50)
    print("开始分类判别分析...")
    start_time = time.time()
    result = fenleipanbie.main(custom_data_dir=custom_data_dir, output_filename=output_file)
    end_time = time.time()
    print(f"分类判别分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result

def flow_analysis(custom_data_dir=None, output_files=None):
    """流量分析"""
    print("="*50)
    print("开始流量分析...")
    start_time = time.time()
    result = flow.main(data_dir=custom_data_dir, output_files=output_files)
    end_time = time.time()
    print(f"流量分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result
    
def saturation_analysis(custom_data_dir=None, output_file=None, cluster_output=None, plot_file=None):
    """饱和度分析"""
    print("="*50)
    print("开始饱和度分析...")
    start_time = time.time()
    result = saturation.main(
        custom_data_dir=custom_data_dir, 
        output_filename=output_file,
        cluster_output=cluster_output,
        plot_filename=plot_file
    )
    end_time = time.time()
    print(f"饱和度分析完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result
    
def predict(custom_data_dir=None, input_file=None, output_model=None, output_results=None, output_plot=None):
    """预测饱和度"""
    print("="*50)
    print("开始预测...")
    start_time = time.time()
    result = prediction_model.main(
        custom_data_dir=custom_data_dir,
        input_filename=input_file,
        output_model=output_model,
        output_results=output_results,
        output_plot=output_plot
    )
    end_time = time.time()
    print(f"预测完成，耗时：{end_time - start_time:.2f}秒")
    print("="*50)
    return result
    
def full_pipeline(custom_data_dir=None, output_dir=None, output_files=None):
    """执行完整分析流程
    
    Args:
        custom_data_dir: 自定义数据目录路径
        output_dir: 输出目录路径，默认与data_dir相同
        output_files: 自定义输出文件名字典
    """
    print("\n" + "="*60)
    print("开始执行服务区饱和度分析完整流程...")
    print("="*60)
    
    total_start_time = time.time()
    
    # 如果未指定输出目录，使用输入目录
    if output_dir is None:
        output_dir = custom_data_dir
    
    # 初始化默认输出文件名
    default_output_files = {
        # 聚类分析
        'cluster_result': "聚类结果.csv",
        
        # 货车参数分析
        'truck_plot': "truck_speed_distribution.png",
        
        # 阈值分析
        'threshold_plot': "threshold_plot.png",
        
        # 速度判别
        'speed_result': "速度判别数据.csv",
        
        # 分类判别
        'classification_result': "分类判别.csv",
        
        # 流量分析
        'flow_adjust': "flow_adjust.csv",
        'etc_flow': "etc_flow.csv",
        'inner_flow': "inner.csv",
        'outer_flow': "outer.csv",
        'ke_inner_flow': "etc_ke_inner.csv",
        'ke_outer_flow': "etc_ke_outer.csv",
        'huo_inner_flow': "etc_huo_inner.csv",
        'huo_outer_flow': "etc_huo_outer.csv",
        'merged_flow': "flow-kehuo-adjusted.xlsx",
        
        # 饱和度分析
        'saturation_result': "merged_flow_saturation_PCA.csv",
        'saturation_clusters': "saturation_clusters.csv",
        'saturation_plot': "saturation_clusters.png",
        
        # 预测
        'prediction_model': "saturation_model.h5",
        'prediction_results': "prediction_results.csv",
        'prediction_plot': "saturation_prediction.png"
    }
    
    # 更新输出文件名（如果提供了）
    if output_files is not None:
        default_output_files.update(output_files)
    
    # 提取流量分析相关输出文件
    flow_output_files = {
        'flow_adjust': default_output_files['flow_adjust'],
        'etc_flow': default_output_files['etc_flow'],
        'inner_flow': default_output_files['inner_flow'],
        'outer_flow': default_output_files['outer_flow'],
        'ke_inner_flow': default_output_files['ke_inner_flow'],
        'ke_outer_flow': default_output_files['ke_outer_flow'],
        'huo_inner_flow': default_output_files['huo_inner_flow'],
        'huo_outer_flow': default_output_files['huo_outer_flow'],
        'merged_flow': default_output_files['merged_flow']
    }
    
    # 1. 数据处理
    process_data(custom_data_dir)
    
    # 2. 聚类分析
    cluster_result = cluster_analysis(
        custom_data_dir=custom_data_dir, 
        output_file=default_output_files['cluster_result']
    )
    
    # 3. 货车参数分析
    truck_params = truck_parameter_analysis(
        custom_data_dir=custom_data_dir,
        output_plot=default_output_files['truck_plot']
    )
    
    # 4. 阈值分析
    threshold = threshold_analysis(
        custom_data_dir=custom_data_dir,
        output_plot=default_output_files['threshold_plot']
    )
    
    # 5. 速度判别
    speed_result = speed_classification(
        custom_data_dir=custom_data_dir,
        output_file=default_output_files['speed_result']
    )
    
    # 6. 分类判别分析
    classification_result = classification_analysis(
        custom_data_dir=custom_data_dir,
        output_file=default_output_files['classification_result']
    )
    
    # 7. 流量分析
    flow_result = flow_analysis(
        custom_data_dir=custom_data_dir,
        output_files=flow_output_files
    )
    
    # 8. 饱和度分析
    saturation_result = saturation_analysis(
        custom_data_dir=custom_data_dir,
        output_file=default_output_files['saturation_result'],
        cluster_output=default_output_files['saturation_clusters'],
        plot_file=default_output_files['saturation_plot']
    )
    
    # 9. 饱和度预测
    prediction_result = predict(
        custom_data_dir=custom_data_dir,
        input_file=default_output_files['merged_flow'],
        output_model=default_output_files['prediction_model'],
        output_results=default_output_files['prediction_results'],
        output_plot=default_output_files['prediction_plot']
    )
    
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
    parser.add_argument('--data-dir', type=str, help='自定义数据目录路径')
    parser.add_argument('--output-dir', type=str, help='自定义输出目录路径')
    
    args = parser.parse_args()
    
    # 获取自定义数据目录路径
    custom_data_dir = args.data_dir if hasattr(args, 'data_dir') and args.data_dir else None
    output_dir = args.output_dir if hasattr(args, 'output_dir') and args.output_dir else custom_data_dir
    
    if args.all:
        full_pipeline(custom_data_dir, output_dir)
    else:
        if args.process:
            process_data(custom_data_dir)
        if args.cluster:
            cluster_analysis(custom_data_dir)
        if args.truck:
            truck_parameter_analysis(custom_data_dir)
        if args.threshold:
            threshold_analysis(custom_data_dir)
        if args.speed:
            speed_classification(custom_data_dir)
        if args.classify:
            classification_analysis(custom_data_dir)
        if args.flow:
            flow_analysis(custom_data_dir)
        if args.analyze:
            saturation_analysis(custom_data_dir)
        if args.predict:
            predict(custom_data_dir)
            
    print("所有任务完成")

if __name__ == "__main__":
    main() 