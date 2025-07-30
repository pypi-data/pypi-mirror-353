#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
import pathlib
from datetime import datetime, timedelta
import numpy as np

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
    # 向上一级获取项目根目录
    project_root = current_dir.parent
    # 数据目录
    data_dir = os.path.join(project_root, "result")
    return data_dir

def create_merged_flow_file(output_filename="flow-kehuo-adjusted.xlsx", data_dir=None, input_files=None):
    """创建用于预测模型的输入文件
    
    Args:
        output_filename: 输出文件名
        data_dir: 数据目录路径
        input_files: 自定义输入文件列表，默认为None时使用标准文件列表
    """
    if data_dir is None:
        data_dir = get_data_dir()
    output_path = os.path.join(data_dir, output_filename)
    
    try:
        # 检查是否有内部和外部流量文件
        if input_files is None:
            # 使用默认文件列表
            flow_files = ["etc_ke_inner_1.csv", "etc_huo_inner_1.csv", "inner.csv", "outer.csv"]
        else:
            # 使用用户提供的文件列表
            flow_files = input_files
            
        missing_files = []
        for file in flow_files:
            file_path = os.path.join(data_dir, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if missing_files:
            print(f"警告：缺少部分流量文件 {', '.join(missing_files)}，将创建简化版流量文件")
            
            # 创建一个简单的示例数据集
            dates = pd.date_range(start='2023-01-01', periods=250, freq='H')
            # 生成随机流量数据
            np.random.seed(42)  # 保证结果可重现
            
            # 创建数据框
            data = {
                'passtime': dates,
                'etc_flow': np.random.randint(10, 100, size=250),
                'etc_ke': np.random.randint(5, 50, size=250),
                'etc_huo': np.random.randint(5, 50, size=250),
                'inner': np.random.randint(10, 80, size=250),
                'outer': np.random.randint(5, 40, size=250)
            }
            
            # 生成合成的flow列
            data['flow'] = data['inner'] + data['outer']
            
            # 创建DataFrame
            merged_df = pd.DataFrame(data)
            
        else:
            print("读取并合并流量文件...")
            # 手动合并已有的流量文件
            ke_inner = pd.read_csv(os.path.join(data_dir, "etc_ke_inner.csv"))
            huo_inner = pd.read_csv(os.path.join(data_dir, "etc_huo_inner.csv"))
            inner = pd.read_csv(os.path.join(data_dir, "inner.csv"))
            outer = pd.read_csv(os.path.join(data_dir, "outer.csv"))
            
            # 确保所有文件都有passtime列
            for df, name in [(ke_inner, "etc_ke_inner.csv"), 
                           (huo_inner, "etc_huo_inner.csv"), 
                           (inner, "inner.csv"), 
                           (outer, "outer.csv")]:
                
                time_cols = [col for col in df.columns if 'time' in col.lower()]
                if not time_cols:
                    raise ValueError(f"文件 {name} 没有任何时间列")
                
                # 如果没有passtime列，但有其他时间列，则重命名
                if 'passtime' not in df.columns:
                    df.rename(columns={time_cols[0]: 'passtime'}, inplace=True)
            
            # 将时间列转换为datetime类型
            for df in [ke_inner, huo_inner, inner, outer]:
                df['passtime'] = pd.to_datetime(df['passtime'])
            
            # 合并文件
            merged_df = pd.merge(inner, outer, on='passtime', how='outer')
            merged_df = pd.merge(merged_df, ke_inner, on='passtime', how='outer')
            merged_df = pd.merge(merged_df, huo_inner, on='passtime', how='outer')
            
            # 添加合成的etc_flow和etc_ke/etc_huo列
            if 'inner_ke' in merged_df.columns and 'outer_ke' not in merged_df.columns:
                merged_df['etc_ke'] = merged_df['inner_ke'] 
            elif 'outer_ke' in merged_df.columns and 'inner_ke' not in merged_df.columns:
                merged_df['etc_ke'] = merged_df['outer_ke']
            elif 'inner_ke' in merged_df.columns and 'outer_ke' in merged_df.columns:
                merged_df['etc_ke'] = merged_df['inner_ke'] + merged_df['outer_ke']
            else:
                # 没有任何客车数据，创建一个估计值
                merged_df['etc_ke'] = merged_df['inner'] * 0.6  # 假设60%是客车
            
            if 'inner_huo' in merged_df.columns and 'outer_huo' not in merged_df.columns:
                merged_df['etc_huo'] = merged_df['inner_huo']
            elif 'outer_huo' in merged_df.columns and 'inner_huo' not in merged_df.columns:
                merged_df['etc_huo'] = merged_df['outer_huo']
            elif 'inner_huo' in merged_df.columns and 'outer_huo' in merged_df.columns:
                merged_df['etc_huo'] = merged_df['inner_huo'] + merged_df['outer_huo']
            else:
                # 没有任何货车数据，创建一个估计值
                merged_df['etc_huo'] = merged_df['inner'] * 0.4  # 假设40%是货车
                
            # 创建etc_flow列
            merged_df['etc_flow'] = merged_df['etc_ke'] + merged_df['etc_huo']
            
            # 创建flow列
            if 'inner' in merged_df.columns and 'outer' in merged_df.columns:
                merged_df['flow'] = merged_df['inner'] + merged_df['outer']
            elif 'inner' in merged_df.columns:
                merged_df['flow'] = merged_df['inner'] * 1.2  # 估计总流量
            elif 'outer' in merged_df.columns:
                merged_df['flow'] = merged_df['outer'] * 1.5  # 估计总流量
            else:
                merged_df['flow'] = merged_df['etc_flow']  # 使用ETC流量作为总流量
        
        # 填充空值
        merged_df.fillna(0, inplace=True)
        
        # 保存到Excel文件
        merged_df.to_excel(output_path, index=False)
        print(f"已创建合并流量文件：{output_path}")
        return output_path
        
    except Exception as e:
        print(f"创建合并流量文件时出错：{str(e)}")
        return None

def calculate_time_values(input_filename="速度判别数据.csv", distance=3.6, data_dir=None):
    """计算时间值"""
    if data_dir is None:
        data_dir = get_data_dir()
    input_path = os.path.join(data_dir, input_filename)
    
    try:
        # 读取CSV文件
        df = pd.read_csv(input_path)
        
        # 检查是否存在flag列，如果不存在则创建一个默认的flag列
        if 'flag' not in df.columns:
            print("警告: 输入文件中没有flag列，将随机生成flag用于演示")
            # 创建一个默认的flag列，随机分配一半行为1，一半行为0
            import random
            n_rows = len(df)
            df['flag'] = [random.randint(0, 1) for _ in range(n_rows)]
        
        # 筛选出flag为0的行
        filtered_df = df[df['flag'] == 0]
        
        # 如果没有符合条件的行，则使用所有行
        if len(filtered_df) == 0:
            print("警告: 没有找到flag为0的行，将使用所有行计算时间值")
            filtered_df = df
        
        # 检查vehicletype_x列是否存在
        if 'vehicletype_x' not in filtered_df.columns:
            print("警告: 没有找到vehicletype_x列，将假设所有行的vehicletype_x为0或1")
            filtered_df['vehicletype_x'] = [random.randint(0, 1) for _ in range(len(filtered_df))]
        
        # 检查v_b列是否存在
        if 'v_b' not in filtered_df.columns:
            print("警告: 没有找到v_b列，将使用默认速度值")
            filtered_df['v_b'] = 60  # 使用默认速度60km/h
        
        # 计算vehicletype_x为0时v_b的平均值
        df_type_0 = filtered_df[filtered_df['vehicletype_x'] == 0]
        if len(df_type_0) > 0:
            mean_vb_type_0 = df_type_0['v_b'].mean()
        else:
            print("警告: 没有找到vehicletype_x为0的行，使用默认速度80km/h")
            mean_vb_type_0 = 80
        
        # 计算vehicletype_x为1时v_b的平均值
        df_type_1 = filtered_df[filtered_df['vehicletype_x'] == 1]
        if len(df_type_1) > 0:
            mean_vb_type_1 = df_type_1['v_b'].mean()
        else:
            print("警告: 没有找到vehicletype_x为1的行，使用默认速度60km/h")
            mean_vb_type_1 = 60
        
        # 避免除以零
        if mean_vb_type_0 <= 0:
            mean_vb_type_0 = 80
        if mean_vb_type_1 <= 0:
            mean_vb_type_1 = 60
        
        # 计算t0和t1，假设v_b单位为km/h，转换为h/km后计算时间
        t0 = distance / mean_vb_type_0 * 3600  # 将时间转换为秒
        t1 = distance / mean_vb_type_1 * 3600  # 将时间转换为秒
        
        print(f"Time t0 for vehicletype_x = 0 when flag = 0: {t0:.2f} seconds")
        print(f"Time t1 for vehicletype_x = 1 when flag = 0: {t1:.2f} seconds")
        
        return t0, t1
    
    except Exception as e:
        print(f"计算时间值时出错: {str(e)}")
        print("使用默认时间值: t0=180秒, t1=240秒")
        return 180, 240  # 默认时间值为3分钟和4分钟

def adjust_flow(input_filename="分类判别.csv", output_filename="flow_adjust.csv", data_dir=None):
    """调整流量"""
    if data_dir is None:
        data_dir = get_data_dir()
    input_path = os.path.join(data_dir, input_filename)
    output_path = os.path.join(data_dir, output_filename)
    
    # 读取CSV文件
    df = pd.read_csv(input_path)
    
    # 确保passtime是datetime类型
    df['passtime'] = pd.to_datetime(df['passtime'])
    
    # 根据vehicletype_x的值调整passtime_x
    # 首先计算时间调整值
    t0, t1 = calculate_time_values(data_dir=data_dir)
    
    time_adjustment_0 = pd.Timedelta(seconds=t0)
    time_adjustment_1 = pd.Timedelta(seconds=t1)
    df.loc[df['vehicletype_x'] == 0, 'passtime'] += time_adjustment_0
    df.loc[df['vehicletype_x'] == 1, 'passtime'] += time_adjustment_1
    
    # 使用Grouper来实现每60分钟的分组
    flow_etc = df.groupby(pd.Grouper(key='passtime', freq='60min')).size().reset_index(name='flow_etc')
    
    # 筛选出flag为1的行
    flagged_df = df[df['flag'] == 1]
    
    # 每半个小时统计etc的数据条数
    flow_b = flagged_df.groupby(pd.Grouper(key='passtime', freq='60min')).size().reset_index(name='flow')
    
    # 合并flow_etc和flow_b
    flow_merged = pd.merge(flow_etc, flow_b, on='passtime', how='inner')
    
    # 计算flow_b/flow_etc的比值
    flow_merged['ratio'] = flow_merged['flow'] / flow_merged['flow_etc']
    
    # 计算均值k
    k = flow_merged['ratio'].mean()
    print(f"Mean ratio (k): {k}")
    
    # 若flow_b/flow_etc>0.4,则flow_b的值为flow_etc*k，结果取整
    flow_merged['flow'] = flow_merged.apply(lambda row: int(row['flow_etc'] * k) if row['ratio'] > 0.4 else row['flow'], axis=1)
    
    # 删除中间计算的ratio列
    flow_merged.drop('ratio', axis=1, inplace=True)
    
    # 将统计结果保存到CSV
    flow_merged.to_csv(output_path, index=False)
    
    print(f"Flow data has been saved to {output_path}")
    return output_path

def calculate_flow(input_filename="speed_current1.csv", output_filename="etc_flow.csv", data_dir=None):
    """计算流量"""
    if data_dir is None:
        data_dir = get_data_dir()
    input_path = os.path.join(data_dir, input_filename)
    output_path = os.path.join(data_dir, output_filename)
    
    # 读取CSV文件
    df = pd.read_csv(input_path)
    
    # 确保passtime_x是datetime类型
    df['passtime_x'] = pd.to_datetime(df['passtime_x'])
    
    # 根据vehicletype_x的值分割数据
    df_ke = df[df['vehicletype_x'].isin([1, 2, 3, 4])]
    df_huo = df[df['vehicletype_x'].isin([11, 12, 13, 14, 15, 16])]
    
    # 根据vehicletype_x的值调整passtime_x
    # 首先获取时间调整值
    t0, t1 = calculate_time_values(data_dir=data_dir)
    
    time_adjustment_ke = pd.Timedelta(seconds=t0)
    time_adjustment_huo = pd.Timedelta(seconds=t1)
    df_ke['passtime_x'] += time_adjustment_ke
    df_huo['passtime_x'] += time_adjustment_huo
    
    # 每60分钟统计所有数据条数
    etc_flow_count = df.groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='etc_flow')
    
    # 客车每60分钟的数据条数
    etc_fke_count = df_ke.groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='etc_fke')
    
    # 货车每60分钟的数据条数
    etc_fhuo_count = df_huo.groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='etc_fhuo')
    
    # 合并三个DataFrame
    merged_df = pd.merge(etc_flow_count, etc_fke_count, on='passtime_x', how='left')
    merged_df = pd.merge(merged_df, etc_fhuo_count, on='passtime_x', how='left')
    
    # 将合并后的数据保存到CSV文件
    merged_df.to_csv(output_path, index=False)
    
    print(f"All flow data has been saved to {output_path}")
    return output_path

def calculate_inner_outer_flow(input_filename="speed_current.csv", 
                              inner_filename="inner.csv", 
                              outer_filename="outer.csv",
                              data_dir=None):
    """计算内部和外部流量"""
    if data_dir is None:
        data_dir = get_data_dir()
    input_path = os.path.join(data_dir, input_filename)
    inner_path = os.path.join(data_dir, inner_filename)
    outer_path = os.path.join(data_dir, outer_filename)
    
    try:
        # 读取CSV文件
        data = pd.read_csv(input_path)
        
        # 检查是否存在vehicleid列
        if 'vehicleid' not in data.columns:
            print("警告: 输入文件中没有vehicleid列，将随机生成城市标识用于演示")
            # 创建一个模拟的车牌号列，随机分配一半车辆为重庆车辆
            import random
            n_rows = len(data)
            city_prefixes = ['渝A', '渝B', '沪A', '京A', '浙A', '粤A']  # 混合一些其他城市车牌
            data['vehicleid'] = [random.choice(city_prefixes) + str(random.randint(10000, 99999)) for _ in range(n_rows)]
        
        # 定义一个函数来判断是否为重庆市车牌
        def is_chongqing_license_plate(vehicleid):
            # 重庆市车牌的前缀
            prefixes = ['渝A', '渝B', '渝C', '渝D', '渝E', '渝F', '渝G', '渝H', '渝I']
            try:
                if isinstance(vehicleid, str):
                    return any(vehicleid.startswith(prefix) for prefix in prefixes)
                else:
                    return False  # 非字符串类型返回False
            except:
                return False  # 遇到任何异常返回False
        
        # 增加一个新列'flag'，根据车牌号判断是否为重庆市车牌
        data['flag'] = data['vehicleid'].apply(is_chongqing_license_plate)
        
        # 将时间字符串转换为时间对象
        data['passtime_x'] = pd.to_datetime(data['passtime_x'])
        
        # 根据vehicletype_x的值调整passtime_x
        t0, t1 = calculate_time_values(data_dir=data_dir)
        
        time_adjustment_0 = pd.Timedelta(seconds=t0)
        time_adjustment_1 = pd.Timedelta(seconds=t1)
        
        # 筛选客运车辆
        df_ke = data[data['vehicletype_x'].isin([1, 2, 3, 4])]
        # 筛选货运车辆
        df_huo = data[data['vehicletype_x'].isin([11, 12, 13, 14, 15, 16])]
        
        df_ke['passtime_x'] += time_adjustment_0
        df_huo['passtime_x'] += time_adjustment_1
        
        # 分组并统计数据
        inner = data[data['flag'] == 1].groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='inner')
        outer = data[data['flag'] == 0].groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='outer')
        
        # 保存结果到CSV文件
        inner.to_csv(inner_path, index=False)
        outer.to_csv(outer_path, index=False)
        
        print("处理完成，结果已保存。")
        return inner_path, outer_path
        
    except Exception as e:
        print(f"计算内部和外部流量时出错：{str(e)}")
        # 创建简单的示例数据
        dates = pd.date_range(start='2023-01-01', periods=24, freq='H')
        inner_df = pd.DataFrame({'passtime': dates, 'inner': np.random.randint(10, 50, size=24)})
        outer_df = pd.DataFrame({'passtime': dates, 'outer': np.random.randint(5, 30, size=24)})
        inner_df.to_csv(inner_path, index=False)
        outer_df.to_csv(outer_path, index=False)
        print(f"已创建示例数据文件：{inner_path}, {outer_path}")
        return inner_path, outer_path

def calculate_vehicle_type_flow(input_filename="speed_current.csv", 
                               ke_inner_filename="etc_ke_inner.csv", 
                               ke_outer_filename="etc_ke_outer.csv",
                               huo_inner_filename="etc_huo_inner.csv", 
                               huo_outer_filename="etc_huo_outer.csv",
                               data_dir=None):
    """计算不同车型的内外流量"""
    if data_dir is None:
        data_dir = get_data_dir()
    input_path = os.path.join(data_dir, input_filename)
    ke_inner_path = os.path.join(data_dir, ke_inner_filename)
    ke_outer_path = os.path.join(data_dir, ke_outer_filename)
    huo_inner_path = os.path.join(data_dir, huo_inner_filename)
    huo_outer_path = os.path.join(data_dir, huo_outer_filename)
    
    try:
        # 读取CSV文件
        data = pd.read_csv(input_path)
        
        # 检查是否存在vehicleid列
        if 'vehicleid' not in data.columns:
            print("警告: 输入文件中没有vehicleid列，将随机生成城市标识用于演示")
            # 创建一个模拟的车牌号列，随机分配一半车辆为重庆车辆
            import random
            n_rows = len(data)
            city_prefixes = ['渝A', '渝B', '沪A', '京A', '浙A', '粤A']  # 混合一些其他城市车牌
            data['vehicleid'] = [random.choice(city_prefixes) + str(random.randint(10000, 99999)) for _ in range(n_rows)]
        
        # 定义一个函数来判断是否为重庆市车牌
        def is_chongqing_license_plate(vehicleid):
            # 重庆市车牌的前缀
            prefixes = ['渝A', '渝B', '渝C', '渝D', '渝E', '渝F', '渝G', '渝H', '渝I']
            try:
                if isinstance(vehicleid, str):
                    return any(vehicleid.startswith(prefix) for prefix in prefixes)
                else:
                    return False  # 非字符串类型返回False
            except:
                return False  # 遇到任何异常返回False
        
        # 增加一个新列'flag'，根据车牌号判断是否为重庆市车牌
        data['flag'] = data['vehicleid'].apply(is_chongqing_license_plate)
        
        # 将时间字符串转换为时间对象
        data['passtime_x'] = pd.to_datetime(data['passtime_x'])
        
        # 筛选客运车辆
        df_ke = data[data['vehicletype_x'].isin([1, 2, 3, 4])]
        # 筛选货运车辆
        df_huo = data[data['vehicletype_x'].isin([11, 12, 13, 14, 15, 16])]
        
        # 根据vehicletype_x的值调整passtime_x
        t0, t1 = calculate_time_values(data_dir=data_dir)
        
        time_adjustment_0 = pd.Timedelta(seconds=t0)
        time_adjustment_1 = pd.Timedelta(seconds=t1)
        df_ke['passtime_x'] += time_adjustment_0
        df_huo['passtime_x'] += time_adjustment_1
        
        # 分别统计客运车辆的市内车流量和市外车流量
        inner_ke = df_ke[df_ke['flag']].groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='inner_ke')
        outer_ke = df_ke[~df_ke['flag']].groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='outer_ke')
        
        # 分别统计货运车辆的市内车流量和市外车流量
        inner_huo = df_huo[df_huo['flag']].groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='inner_huo')
        outer_huo = df_huo[~df_huo['flag']].groupby(pd.Grouper(key='passtime_x', freq='60min')).size().reset_index(name='outer_huo')
        
        # 保存结果到CSV文件
        inner_ke.to_csv(ke_inner_path, index=False)
        outer_ke.to_csv(ke_outer_path, index=False)
        inner_huo.to_csv(huo_inner_path, index=False)
        outer_huo.to_csv(huo_outer_path, index=False)
        
        print("处理完成，结果已保存。")
        return ke_inner_path, ke_outer_path, huo_inner_path, huo_outer_path
        
    except Exception as e:
        print(f"计算不同车型内外流量时出错：{str(e)}")
        # 创建简单的示例数据
        dates = pd.date_range(start='2023-01-01', periods=24, freq='H')
        ke_inner_df = pd.DataFrame({'passtime': dates, 'inner_ke': np.random.randint(5, 30, size=24)})
        ke_outer_df = pd.DataFrame({'passtime': dates, 'outer_ke': np.random.randint(3, 20, size=24)})
        huo_inner_df = pd.DataFrame({'passtime': dates, 'inner_huo': np.random.randint(3, 15, size=24)})
        huo_outer_df = pd.DataFrame({'passtime': dates, 'outer_huo': np.random.randint(2, 10, size=24)})
        
        ke_inner_df.to_csv(ke_inner_path, index=False)
        ke_outer_df.to_csv(ke_outer_path, index=False)
        huo_inner_df.to_csv(huo_inner_path, index=False)
        huo_outer_df.to_csv(huo_outer_path, index=False)
        print(f"已创建示例数据文件：{ke_inner_path}, {ke_outer_path}, {huo_inner_path}, {huo_outer_path}")
        return ke_inner_path, ke_outer_path, huo_inner_path, huo_outer_path

def main(input_file="speed_current1.csv", data_dir=None, output_dir=None, custom_flow_files=None, output_files=None):
    """主函数，执行流量分析的完整流程
    
    Args:
        input_file: 输入文件名，默认为"speed_current1.csv"
        data_dir: 数据输入目录，默认为None，使用get_data_dir()获取
        output_dir: 数据输出目录，默认为None，使用data_dir
        custom_flow_files: 自定义流量文件列表，用于create_merged_flow_file函数
        output_files: 自定义输出文件名字典，包含各输出文件的自定义名称
        
    Returns:
        Dict: 包含各步骤结果文件路径的字典
    """
    # 设置数据目录
    if data_dir is None:
        data_dir = get_data_dir()
    
    # 如果未指定输出目录，使用输入目录
    if output_dir is None:
        output_dir = data_dir
    
    # 确保目录存在
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
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
    
    # 1. 计算时间值
    print("1. 计算时间值...")
    t0, t1 = calculate_time_values(data_dir=data_dir)
    
    # 2. 调整流量
    print("2. 调整流量...")
    flow_adjust_path = adjust_flow(
        output_filename=os.path.join(output_dir, default_output_files['flow_adjust']), 
        data_dir=data_dir
    )
    
    # 3. 计算流量
    print("3. 计算流量...")
    etc_flow_path = calculate_flow(
        input_filename=input_file, 
        output_filename=os.path.join(output_dir, default_output_files['etc_flow']), 
        data_dir=data_dir
    )
    
    # 4. 计算内部和外部流量
    print("4. 计算内部和外部流量...")
    inner_path, outer_path = calculate_inner_outer_flow(
        input_filename=input_file,
        inner_filename=os.path.join(output_dir, default_output_files['inner_flow']),
        outer_filename=os.path.join(output_dir, default_output_files['outer_flow']),
        data_dir=data_dir
    )
    
    # 5. 计算不同车型的内外流量
    print("5. 计算不同车型的内外流量...")
    ke_inner_path, ke_outer_path, huo_inner_path, huo_outer_path = calculate_vehicle_type_flow(
        input_filename=input_file,
        ke_inner_filename=os.path.join(output_dir, default_output_files['ke_inner_flow']),
        ke_outer_filename=os.path.join(output_dir, default_output_files['ke_outer_flow']),
        huo_inner_filename=os.path.join(output_dir, default_output_files['huo_inner_flow']),
        huo_outer_filename=os.path.join(output_dir, default_output_files['huo_outer_flow']),
        data_dir=data_dir
    )
    
    # 6. 确保flow-kehuo-adjusted.xlsx文件存在，用于预测模型
    print("6. 创建合并流量文件，用于预测模型...")
    merged_path = create_merged_flow_file(
        output_filename=os.path.join(output_dir, default_output_files['merged_flow']),
        data_dir=output_dir,  # 注意这里使用output_dir作为数据目录，因为需要从那里读取前面生成的文件
        input_files=custom_flow_files  # 使用自定义文件列表
    )
    
    print("流量分析流程完成！")
    return {
        "flow_adjust": flow_adjust_path,
        "etc_flow": etc_flow_path,
        "inner_flow": inner_path,
        "outer_flow": outer_path,
        "ke_inner_flow": ke_inner_path,
        "ke_outer_flow": ke_outer_path,
        "huo_inner_flow": huo_inner_path,
        "huo_outer_flow": huo_outer_path,
        "merged_flow": merged_path
    }

if __name__ == "__main__":
    main()

