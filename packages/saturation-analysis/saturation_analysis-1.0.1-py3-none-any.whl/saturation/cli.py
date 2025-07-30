#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务区饱和度分析系统 - 命令行接口
"""

import argparse
import os
import sys
import time
from . import api

def main():
    """命令行主入口点"""
    parser = argparse.ArgumentParser(description='服务区饱和度分析系统')

    # 全局参数
    parser.add_argument('--data-dir', help='数据目录路径')
    parser.add_argument('--output-dir', help='输出目录路径')

    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='要执行的命令')

    # 完整流程命令
    full_pipeline_parser = subparsers.add_parser('run-all', help='执行完整分析流程')
    
    # 数据处理命令
    process_parser = subparsers.add_parser('process', help='执行数据处理')
    process_parser.add_argument('--input', help='输入文件')
    process_parser.add_argument('--output', help='输出文件')
    
    # 聚类分析命令
    cluster_parser = subparsers.add_parser('cluster', help='执行聚类分析')
    cluster_parser.add_argument('--input', default='total.csv', help='输入文件，默认为total.csv')
    cluster_parser.add_argument('--output', default='聚类结果.csv', help='输出文件，默认为聚类结果.csv')
    cluster_parser.add_argument('--components', type=int, default=2, help='聚类数量，默认为2')
    cluster_parser.add_argument('--test-size', type=float, default=0.2, help='测试集比例，默认为0.2')
    cluster_parser.add_argument('--plot', action='store_true', help='生成聚类图表')

    # 分类判别命令
    classify_parser = subparsers.add_parser('classify', help='执行分类判别')
    classify_parser.add_argument('--cluster-file', default='聚类结果.csv', help='聚类结果文件')
    classify_parser.add_argument('--speed-file', default='速度判别数据.csv', help='速度判别数据文件')
    classify_parser.add_argument('--output', default='分类判别.csv', help='输出文件')
    
    # 阈值分析命令
    threshold_parser = subparsers.add_parser('threshold', help='执行阈值分析')
    threshold_parser.add_argument('--mu1', type=float, default=69.24, help='分布1均值')
    threshold_parser.add_argument('--mu2', type=float, default=15.42, help='分布2均值')
    threshold_parser.add_argument('--sigma1', type=float, default=10.22, help='分布1标准差')
    threshold_parser.add_argument('--sigma2', type=float, default=9.47, help='分布2标准差')
    threshold_parser.add_argument('--w1', type=float, default=0.7, help='分布1权重')
    threshold_parser.add_argument('--w2', type=float, default=0.3, help='分布2权重')
    threshold_parser.add_argument('--no-plot', action='store_true', help='不生成图表')
    
    # 货车参数分析命令
    truck_parser = subparsers.add_parser('truck', help='执行货车参数分析')
    truck_parser.add_argument('--input', default='speed_current.csv', help='输入文件')
    truck_parser.add_argument('--output-plot', default='truck_speed_distribution.png', help='图表输出文件')
    truck_parser.add_argument('--no-plot', action='store_true', help='不生成图表')
    
    # 流量分析命令
    flow_parser = subparsers.add_parser('flow', help='执行流量分析')
    flow_parser.add_argument('--input', default='speed_current1.csv', help='输入文件')
    
    # 饱和度分析命令
    saturation_parser = subparsers.add_parser('saturation', help='执行饱和度分析')
    saturation_parser.add_argument('--ke-flow', default='ke_flow1.csv', help='客车流量文件')
    saturation_parser.add_argument('--huo-flow', default='huo_flow1.csv', help='货车流量文件')
    saturation_parser.add_argument('--output', default='merged_flow_saturation_PCA.csv', help='输出文件')
    
    # 预测命令
    predict_parser = subparsers.add_parser('predict', help='执行预测')
    predict_parser.add_argument('--input', default='flow-kehuo-adjusted.xlsx', help='输入文件')
    predict_parser.add_argument('--output-model', default='saturation_model.h5', help='模型输出文件')
    predict_parser.add_argument('--train-size', type=int, default=200, help='训练集大小')
    predict_parser.add_argument('--time-steps', type=int, default=5, help='时间步长')
    predict_parser.add_argument('--input-dims', type=int, default=6, help='输入维度')
    predict_parser.add_argument('--lstm-units', type=int, default=64, help='LSTM单元数')
    predict_parser.add_argument('--epochs', type=int, default=100, help='训练轮数')
    predict_parser.add_argument('--batch-size', type=int, default=64, help='批处理大小')
    predict_parser.add_argument('--no-plot', action='store_true', help='不生成图表')

    # 解析参数
    args = parser.parse_args()
    
    # 设置数据目录
    if args.data_dir:
        api.set_data_dir(args.data_dir)
    
    # 设置输出目录
    output_dir = args.output_dir if args.output_dir else api.get_data_dir()
    
    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 执行对应的命令
    if args.command == 'run-all':
        # 执行完整流程
        print("开始执行完整分析流程...")
        start_time = time.time()
        results = api.run_full_pipeline(data_dir=args.data_dir, output_dir=output_dir)
        end_time = time.time()
        print(f"分析完成，总耗时: {end_time - start_time:.2f} 秒")
        
    elif args.command == 'process':
        # 执行数据处理
        print("开始数据处理...")
        start_time = time.time()
        result = api.process_data(
            input_file=args.input, 
            output_file=args.output,
            data_dir=args.data_dir
        )
        end_time = time.time()
        print(f"数据处理完成，结果保存在: {result}")
        print(f"处理耗时: {end_time - start_time:.2f} 秒")
        
    elif args.command == 'cluster':
        # 执行聚类分析
        print("开始聚类分析...")
        start_time = time.time()
        result = api.cluster_analysis(
            input_file=args.input,
            output_file=args.output,
            n_components=args.components,
            test_size=args.test_size,
            plot=args.plot,
            data_dir=args.data_dir
        )
        end_time = time.time()
        print(f"聚类分析完成，结果保存在: {result}")
        print(f"分析耗时: {end_time - start_time:.2f} 秒")
        
    elif args.command == 'classify':
        # 执行分类判别
        print("开始分类判别...")
        start_time = time.time()
        result = api.classify_data_by_cluster(
            cluster_file=args.cluster_file,
            speed_file=args.speed_file,
            output_file=args.output,
            data_dir=args.data_dir
        )
        end_time = time.time()
        print(f"分类判别完成，结果保存在: {result}")
        print(f"分析耗时: {end_time - start_time:.2f} 秒")
        
    elif args.command == 'threshold':
        # 执行阈值分析
        print("开始阈值分析...")
        start_time = time.time()
        result = api.analyze_threshold(
            mu1=args.mu1,
            mu2=args.mu2,
            sigma1=args.sigma1,
            sigma2=args.sigma2,
            w1=args.w1,
            w2=args.w2,
            save_plot=not args.no_plot,
            data_dir=args.data_dir
        )
        end_time = time.time()
        print(f"阈值分析完成，结果为: {result:.4f}")
        print(f"分析耗时: {end_time - start_time:.2f} 秒")
        
    elif args.command == 'truck':
        # 执行货车参数分析
        print("开始货车参数分析...")
        start_time = time.time()
        result = api.analyze_truck_params(
            input_file=args.input,
            plot=not args.no_plot,
            output_plot=args.output_plot,
            data_dir=args.data_dir
        )
        end_time = time.time()
        print(f"货车参数分析完成")
        print(f"分析耗时: {end_time - start_time:.2f} 秒")
        
    elif args.command == 'flow':
        # 执行流量分析
        print("开始流量分析...")
        start_time = time.time()
        result = api.analyze_flow(
            input_file=args.input,
            data_dir=args.data_dir,
            output_dir=output_dir
        )
        end_time = time.time()
        print(f"流量分析完成，结果保存在: {output_dir}")
        print(f"分析耗时: {end_time - start_time:.2f} 秒")
        
    elif args.command == 'saturation':
        # 执行饱和度分析
        print("开始饱和度分析...")
        start_time = time.time()
        result = api.analyze_saturation_data(
            ke_flow_file=args.ke_flow,
            huo_flow_file=args.huo_flow,
            output_file=args.output,
            data_dir=args.data_dir
        )
        end_time = time.time()
        print(f"饱和度分析完成，结果保存在: {result}")
        print(f"分析耗时: {end_time - start_time:.2f} 秒")
        
    elif args.command == 'predict':
        # 执行预测
        print("开始预测...")
        start_time = time.time()
        result = api.predict(
            input_file=args.input,
            output_model=args.output_model,
            train_size=args.train_size,
            time_steps=args.time_steps,
            input_dims=args.input_dims,
            lstm_units=args.lstm_units,
            epochs=args.epochs,
            batch_size=args.batch_size,
            save_plot=not args.no_plot,
            data_dir=args.data_dir
        )
        end_time = time.time()
        print(f"预测完成，结果保存在数据目录中")
        print(f"预测耗时: {end_time - start_time:.2f} 秒")
        
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 