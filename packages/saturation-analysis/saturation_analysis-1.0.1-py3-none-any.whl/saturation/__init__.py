"""
服务区饱和度分析系统 - 提供服务区流量和饱和度分析功能的Python包

主要模块:
- data_process: 数据处理
- julei: 聚类分析
- fenleipanbie: 分类判别
- yuzhi: 阈值分析
- huo_canshu: 货车参数分析
- flow: 流量分析
- saturation: 饱和度分析
- prediction: 饱和度预测
"""

__version__ = '1.0.0'

# 导入主要API函数
from .enJud.data_process import complete_data_processing_pipeline, process_initial_data
from .enJud.julei import perform_clustering
from .enJud.fenleipanbie import classify_data
from .enJud.yuzhi import calculate_threshold
from .enJud.huo_canshu import analyze_truck_parameters
from .flow import create_merged_flow_file, calculate_flow, calculate_inner_outer_flow, calculate_vehicle_type_flow
from .satAna.saturation import analyze_saturation, cluster_saturation
from .pre.预测模型 import predict_saturation

# 模块名称映射，便于API使用
modules = {
    'data_process': '数据处理模块',
    'julei': '聚类分析模块',
    'fenleipanbie': '分类判别模块',
    'yuzhi': '阈值分析模块',
    'huo_canshu': '货车参数分析模块',
    'flow': '流量分析模块',
    'saturation': '饱和度分析模块',
    'prediction': '预测模块'
}

# 主要API函数
__all__ = [
    # 数据处理
    'complete_data_processing_pipeline',
    'process_initial_data',
    
    # 聚类分析
    'perform_clustering',
    
    # 分类判别
    'classify_data',
    
    # 阈值分析
    'calculate_threshold',
    
    # 货车参数分析
    'analyze_truck_parameters',
    
    # 流量分析
    'create_merged_flow_file',
    'calculate_flow',
    'calculate_inner_outer_flow',
    'calculate_vehicle_type_flow',
    
    # 饱和度分析
    'analyze_saturation',
    'cluster_saturation',
    
    # 预测
    'predict_saturation'
] 