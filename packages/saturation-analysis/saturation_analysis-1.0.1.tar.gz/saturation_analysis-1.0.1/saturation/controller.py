#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务区饱和度分析系统 - 控制器

提供统一的控制接口，允许用户通过简单的方法调用各种分析功能，
并支持自定义输入输出路径和参数。
"""

import os
import logging
import argparse
import sys
from typing import Dict, Optional, Union, List, Tuple, Any

from saturation.utils.config import get_config, set_config, update_config
from saturation.utils.file_utils import ensure_dir_exists, get_absolute_path, is_valid_file

from saturation.enJud import data_process, julei, fenleipanbie, panbie, yuzhi, huo_canshu
from saturation import flow
from saturation.satAna import saturation
from saturation.pre import 预测模型 as prediction_model

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SaturationController:
    """服务区饱和度分析控制器
    
    提供一个统一的接口来控制和执行所有分析功能。
    """
    
    def __init__(self, data_dir: Optional[str] = None, output_dir: Optional[str] = None):
        """
        初始化控制器
        
        Args:
            data_dir (str, optional): 数据目录路径
            output_dir (str, optional): 输出目录路径
        """
        # 设置数据和输出目录
        if data_dir:
            set_config('data_dir', ensure_dir_exists(data_dir))
        
        if output_dir:
            set_config('output_dir', ensure_dir_exists(output_dir))
        else:
            # 如果没有指定输出目录，使用数据目录
            set_config('output_dir', get_config('data_dir'))
        
        logger.info(f"初始化控制器完成，数据目录: {get_config('data_dir')}, 输出目录: {get_config('output_dir')}")
    
    def set_data_dir(self, data_dir: str) -> str:
        """
        设置数据目录
        
        Args:
            data_dir (str): 数据目录路径
            
        Returns:
            str: 设置后的数据目录路径
        """
        set_config('data_dir', ensure_dir_exists(data_dir))
        logger.info(f"数据目录已设置为: {data_dir}")
        return data_dir
    
    def set_output_dir(self, output_dir: str) -> str:
        """
        设置输出目录
        
        Args:
            output_dir (str): 输出目录路径
            
        Returns:
            str: 设置后的输出目录路径
        """
        set_config('output_dir', ensure_dir_exists(output_dir))
        logger.info(f"输出目录已设置为: {output_dir}")
        return output_dir
    
    def process_data(self, input_file: str, output_file: Optional[str] = None) -> str:
        """
        处理原始数据
        
        Args:
            input_file (str): 输入文件名或路径
            output_file (str, optional): 输出文件名或路径
            
        Returns:
            str: 处理后的文件路径
        """
        logger.info(f"开始处理数据: {input_file}")
        
        # 确保输入文件路径正确
        input_path = get_absolute_path(input_file, get_config('data_dir'))
        
        # 如果未指定输出文件，则使用默认名称
        if output_file is None:
            output_file = "processed_data.csv"
        
        # 确保输出路径正确
        output_path = get_absolute_path(output_file, get_config('output_dir'))
        
        # 处理数据
        result = data_process.process_initial_data(input_filename=input_path, output_filename=output_path)
        
        logger.info(f"数据处理完成，结果保存在: {result}")
        return result
    
    def analyze_flow(self, input_file: str, output_file: Optional[str] = None) -> Dict:
        """
        分析流量
        
        Args:
            input_file (str): 输入文件名或路径
            output_file (str, optional): 输出文件名或路径
            
        Returns:
            Dict: 流量分析结果
        """
        logger.info(f"开始流量分析: {input_file}")
        
        # 确保输入文件路径正确
        input_path = get_absolute_path(input_file, get_config('data_dir'))
        
        # 获取数据目录和输出目录
        data_dir = get_config('data_dir')
        output_dir = get_config('output_dir')
        
        # 调用修改后的flow.main()函数，支持自定义路径
        result = flow.main(
            input_file=input_path,
            data_dir=data_dir,
            output_dir=output_dir
        )
        
        logger.info("流量分析完成")
        return result
    
    def analyze_saturation(self, ke_flow_file: str, huo_flow_file: str, 
                         output_file: Optional[str] = None) -> Tuple:
        """
        分析饱和度
        
        Args:
            ke_flow_file (str): 客车流量文件名或路径
            huo_flow_file (str): 货车流量文件名或路径
            output_file (str, optional): 输出文件名或路径
            
        Returns:
            Tuple: 饱和度分析结果
        """
        logger.info(f"开始饱和度分析")
        
        # 确保文件路径正确
        ke_flow_path = get_absolute_path(ke_flow_file, get_config('data_dir'))
        huo_flow_path = get_absolute_path(huo_flow_file, get_config('data_dir'))
        
        # 如果未指定输出文件，则使用默认名称
        if output_file is None:
            output_file = "saturation_analysis.csv"
        
        # 确保输出路径正确
        output_path = get_absolute_path(output_file, get_config('output_dir'))
        
        # 分析饱和度
        result = saturation.main(
            ke_flow_filename=ke_flow_path,
            huo_flow_filename=huo_flow_path,
            output_filename=output_path
        )
        
        logger.info("饱和度分析完成")
        return result
    
    def predict_saturation(self, input_file: str, output_model: Optional[str] = None,
                         output_file: Optional[str] = None, **kwargs) -> Dict:
        """
        预测饱和度
        
        Args:
            input_file (str): 输入文件名或路径
            output_model (str, optional): 模型保存路径
            output_file (str, optional): 输出文件名或路径
            **kwargs: 其他参数，如epochs, batch_size等
            
        Returns:
            Dict: 预测结果
        """
        logger.info(f"开始饱和度预测: {input_file}")
        
        # 确保输入文件路径正确
        input_path = get_absolute_path(input_file, get_config('data_dir'))
        
        # 预测饱和度
        result = prediction_model.main(
            input_filename=input_path,
            output_model=output_model,
            **kwargs
        )
        
        logger.info("饱和度预测完成")
        return result
    
    def run_complete_pipeline(self, input_file: str, output_dir: Optional[str] = None) -> Dict:
        """
        运行完整分析流程
        
        Args:
            input_file (str): 输入文件名或路径
            output_dir (str, optional): 输出目录路径
            
        Returns:
            Dict: 包含各步骤结果的字典
        """
        logger.info(f"开始执行完整分析流程: {input_file}")
        
        # 如果指定了输出目录，则设置它
        if output_dir:
            self.set_output_dir(output_dir)
        
        # 确保输入文件路径正确
        input_path = get_absolute_path(input_file, get_config('data_dir'))
        
        # 运行完整流程
        # TODO: 实现更灵活的完整流程，各个步骤使用自定义路径
        
        logger.info("完整分析流程执行完毕")
        return {
            "status": "success",
            "output_dir": get_config('output_dir')
        }


# 创建默认控制器实例，便于直接导入使用
default_controller = SaturationController()

# 简化函数，直接使用默认控制器
def set_data_dir(data_dir: str) -> str:
    """设置数据目录"""
    return default_controller.set_data_dir(data_dir)

def set_output_dir(output_dir: str) -> str:
    """设置输出目录"""
    return default_controller.set_output_dir(output_dir)

def process_data(input_file: str, output_file: Optional[str] = None) -> str:
    """处理数据"""
    return default_controller.process_data(input_file, output_file)

def analyze_flow(input_file: str, output_file: Optional[str] = None) -> Dict:
    """分析流量"""
    return default_controller.analyze_flow(input_file, output_file)

def analyze_saturation(ke_flow_file: str, huo_flow_file: str, output_file: Optional[str] = None) -> Tuple:
    """分析饱和度"""
    return default_controller.analyze_saturation(ke_flow_file, huo_flow_file, output_file)

def predict_saturation(input_file: str, output_model: Optional[str] = None,
                     output_file: Optional[str] = None, **kwargs) -> Dict:
    """预测饱和度"""
    return default_controller.predict_saturation(input_file, output_model, output_file, **kwargs)

def run_complete_pipeline(input_file: str, output_dir: Optional[str] = None) -> Dict:
    """运行完整分析流程"""
    return default_controller.run_complete_pipeline(input_file, output_dir)


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description="服务区饱和度分析控制器")
    
    # 通用参数
    parser.add_argument('--data-dir', type=str, help='数据目录路径')
    parser.add_argument('--output-dir', type=str, help='输出目录路径')
    
    # 创建子命令
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # 处理数据子命令
    process_parser = subparsers.add_parser('process', help='处理原始数据')
    process_parser.add_argument('--input', type=str, required=True, help='输入文件路径')
    process_parser.add_argument('--output', type=str, help='输出文件路径')
    
    # 流量分析子命令
    flow_parser = subparsers.add_parser('flow', help='分析流量')
    flow_parser.add_argument('--input', type=str, required=True, help='输入文件路径')
    flow_parser.add_argument('--output', type=str, help='输出文件路径')
    
    # 饱和度分析子命令
    saturation_parser = subparsers.add_parser('saturation', help='分析饱和度')
    saturation_parser.add_argument('--ke-flow', type=str, required=True, help='客车流量文件路径')
    saturation_parser.add_argument('--huo-flow', type=str, required=True, help='货车流量文件路径')
    saturation_parser.add_argument('--output', type=str, help='输出文件路径')
    
    # 预测子命令
    predict_parser = subparsers.add_parser('predict', help='预测饱和度')
    predict_parser.add_argument('--input', type=str, required=True, help='输入文件路径')
    predict_parser.add_argument('--model', type=str, help='模型保存路径')
    predict_parser.add_argument('--epochs', type=int, default=100, help='训练轮数')
    predict_parser.add_argument('--batch-size', type=int, default=64, help='批次大小')
    
    # 完整流程子命令
    pipeline_parser = subparsers.add_parser('pipeline', help='运行完整分析流程')
    pipeline_parser.add_argument('--input', type=str, required=True, help='输入文件路径')
    
    # 解析参数
    args = parser.parse_args()
    
    # 创建控制器
    ctrl = SaturationController(
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )
    
    # 根据子命令执行相应操作
    if args.command == 'process':
        result = ctrl.process_data(
            input_file=args.input,
            output_file=args.output
        )
        print(f"数据处理完成，结果保存在: {result}")
    
    elif args.command == 'flow':
        result = ctrl.analyze_flow(
            input_file=args.input,
            output_file=args.output
        )
        print(f"流量分析完成，结果: {result}")
    
    elif args.command == 'saturation':
        result = ctrl.analyze_saturation(
            ke_flow_file=args.ke_flow,
            huo_flow_file=args.huo_flow,
            output_file=args.output
        )
        print(f"饱和度分析完成，结果: {result}")
    
    elif args.command == 'predict':
        result = ctrl.predict_saturation(
            input_file=args.input,
            output_model=args.model,
            epochs=args.epochs,
            batch_size=args.batch_size
        )
        print(f"饱和度预测完成，结果: {result}")
    
    elif args.command == 'pipeline':
        result = ctrl.run_complete_pipeline(
            input_file=args.input
        )
        print(f"完整分析流程执行完毕，结果: {result}")
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 