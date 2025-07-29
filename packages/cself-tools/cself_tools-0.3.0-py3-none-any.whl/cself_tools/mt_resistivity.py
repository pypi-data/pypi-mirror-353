import cx_Oracle
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import ScalarFormatter, FuncFormatter
import math
from datetime import datetime
import os
from typing import Dict, List, Optional, Tuple, Union


# 设置matplotlib参数，提高图表质量
def set_plot_style():
    """设置matplotlib的绘图样式以提高图表质量"""
    matplotlib.rcParams['font.family'] = 'serif'
    matplotlib.rcParams['font.serif'] = ['STSong']
    plt.rcParams['mathtext.fontset'] = 'stix'  # 使用STIX数学字体
    plt.rcParams['axes.linewidth'] = 1.2  # 轴线宽度
    plt.rcParams['axes.grid'] = True  # 显示网格
    plt.rcParams['grid.alpha'] = 0.3  # 网格透明度
    plt.rcParams['grid.linestyle'] = '--'  # 网格线型
    plt.rcParams['xtick.major.size'] = 6  # x轴主刻度大小
    plt.rcParams['xtick.minor.size'] = 3  # x轴次刻度大小
    plt.rcParams['ytick.major.size'] = 6  # y轴主刻度大小
    plt.rcParams['ytick.minor.size'] = 3  # y轴次刻度大小
    plt.rcParams['xtick.major.width'] = 1.2  # x轴主刻度宽度
    plt.rcParams['ytick.major.width'] = 1.2  # y轴主刻度宽度
    plt.rcParams['xtick.direction'] = 'in'  # x轴刻度朝内
    plt.rcParams['ytick.direction'] = 'in'  # y轴刻度朝内


def init_oracle_client(lib_dir: str = 'C:/instantclient'):
    """初始化Oracle客户端
    
    Args:
        lib_dir: Oracle客户端库目录路径
    """
    cx_Oracle.init_oracle_client(lib_dir=lib_dir)

    # 输出Oracle客户端版本和配置信息
    client_version = ".".join(str(i) for i in cx_Oracle.clientversion())
    print(f"Oracle客户端初始化成功:")
    print(f"- 客户端版本: {client_version}")
    print(f"- 客户端路径: {lib_dir}")

    # 尝试获取更多配置信息
    try:
        import os
        if os.path.exists(lib_dir):
            dll_files = [f for f in os.listdir(lib_dir) if f.endswith('.dll')]
            print(f"- 客户端DLL文件: {', '.join(dll_files[:5])}" +
                  (f" 等{len(dll_files)}个文件" if len(dll_files) > 5 else ""))
    except Exception as e:
        print(f"- 无法获取更多客户端信息: {str(e)}")


def query_data(
    start_time: str,
    end_time: str,
    station_id: str,
    point_id: str,
    frequency: int,
    db_connection: Optional[Union[cx_Oracle.Connection, str]] = None,
    table_name: str = "QZDATA.QZ_CP_372_90_AVG",  # 可配置的表名
    date_column: str = "STARTDATE",  # 可配置的日期列名
    value_column: str = "RYX",  # 可配置的值列名
    stdv_column: str = "RYXSTDV",  # 可配置的标准差列名
    station_column: str = "STATIONID",  # 可配置的站点ID列名
    point_column: str = "POINTID",  # 可配置的点位ID列名
    freq_column: str = "FREQUENCIES"  # 可配置的频率列名
) -> Optional[pd.DataFrame]:
    """查询Oracle数据库获取极低频视电阻率数据
    
    Args:
        start_time: 开始时间，格式为 "YYYY-MM-DD HH:MM:SS"
        end_time: 结束时间，格式为 "YYYY-MM-DD HH:MM:SS"
        station_id: 站点ID
        point_id: 点位ID
        frequency: 频率(Hz)
        db_connection: 数据库连接对象或连接名称
        table_name: 数据表名，默认为 "QZDATA.QZ_CP_372_90_AVG"
        date_column: 日期列名，默认为 "STARTDATE"
        value_column: 值列名，默认为 "RYX"
        stdv_column: 标准差列名，默认为 "RYXSTDV"
        station_column: 站点ID列名，默认为 "STATIONID"
        point_column: 点位ID列名，默认为 "POINTID"
        freq_column: 频率列名，默认为 "FREQUENCIES"
        
    Returns:
        包含视电阻率数据的DataFrame或None（查询失败时）
    """
    try:
        # 如果传入的是连接名称字符串，使用addereq库连接
        if isinstance(db_connection, str):
            try:
                from addereq import fetching as tsf
                connection = tsf.conn_to_Oracle(db_connection)
            except ImportError:
                print("警告: addereq模块不可用，请提供数据库连接对象")
                return None
        # 如果已提供连接对象，直接使用
        elif isinstance(db_connection, cx_Oracle.Connection):
            connection = db_connection
        # 如果未提供连接信息，尝试使用默认连接
        else:
            try:
                from addereq import fetching as tsf
                connection = tsf.conn_to_Oracle('DB-Shandong-12')
            except ImportError:
                print("警告: addereq模块不可用，请提供数据库连接对象")
                return None

        cursor = connection.cursor()

        # 构建动态SQL查询
        sql = f"""
        SELECT {date_column}, {value_column}, {stdv_column}
        FROM {table_name}
        WHERE {date_column} BETWEEN TO_DATE(:start_time, 'YYYY-MM-DD HH24:MI:SS')
                            AND TO_DATE(:end_time, 'YYYY-MM-DD HH24:MI:SS')
        AND {station_column} = :station_id
        AND {point_column} = :point_id
        AND {freq_column} = :frequency
        ORDER BY {date_column}
        """

        # 执行查询
        cursor.execute(
            sql, {
                'start_time': start_time,
                'end_time': end_time,
                'station_id': station_id,
                'point_id': point_id,
                'frequency': frequency
            })

        # 获取结果
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()

        # 关闭连接
        cursor.close()

        # 如果连接是在函数内部创建的，则关闭连接
        if db_connection is None or isinstance(db_connection, str):
            connection.close()

        # 转换为DataFrame
        df = pd.DataFrame(data, columns=columns)

        # 确保值和标准差列是浮点数类型
        df[value_column] = pd.to_numeric(df[value_column], errors='coerce')
        df[stdv_column] = pd.to_numeric(df[stdv_column], errors='coerce')

        return df

    except Exception as e:
        print(f"数据库查询错误: {str(e)}")
        return None


def preprocess_data(
        df: pd.DataFrame,
        frequency: int,
        value_column: str = "RYX",  # 添加可配置的列名参数
        mad_factor: float = 50.0,
        verbose: bool = True) -> pd.DataFrame:
    """使用中位数绝对偏差(MAD)方法过滤异常值
    
    Args:
        df: 输入数据DataFrame
        frequency: 频率(Hz)，用于日志输出
        value_column: 值列名，默认为 "RYX"
        mad_factor: MAD系数，用于确定异常值阈值
        verbose: 是否输出处理信息
        
    Returns:
        处理后的DataFrame
    """
    if df is None or df.empty:
        return df

    # 保存原始数据行数
    original_count = len(df)

    # 计算值列的中位数
    median_value = df[value_column].median()

    # 计算每个值与中位数的绝对偏差
    mad = np.median(np.abs(df[value_column] - median_value))

    # 设置上下限
    lower_bound = max(0, median_value - mad_factor * mad)  # 确保下限不小于0
    upper_bound = median_value + mad_factor * mad

    # 过滤掉超出范围的数据
    df = df[(df[value_column] >= lower_bound)
            & (df[value_column] <= upper_bound)]

    # 输出过滤后的数据行数
    if verbose:
        filtered_count = len(df)
        removed_count = original_count - filtered_count
        print(
            f"{frequency}Hz数据预处理: 过滤掉 {removed_count} 条记录 (从 {original_count} 到 {filtered_count}), "
            f"阈值范围: [{lower_bound:.2f}, {upper_bound:.2f}]")

    return df


def calculate_moving_average(
    df: pd.DataFrame,
    window_days: int,
    date_column: str = "STARTDATE",  # 添加可配置的日期列名
    value_column: str = "RYX",  # 添加可配置的值列名
    stdv_column: str = "RYXSTDV",  # 添加可配置的标准差列名
    ma_value_column: str = "MA_RYX",  # 添加可配置的移动平均值列名
    ma_stdv_column: str = "MA_RYXSTDV"  # 添加可配置的移动平均标准差列名
) -> Optional[pd.DataFrame]:
    """计算移动平均
    
    Args:
        df: 输入数据DataFrame
        window_days: 移动平均窗口大小（天数）
        date_column: 日期列名，默认为 "STARTDATE"
        value_column: 值列名，默认为 "RYX"
        stdv_column: 标准差列名，默认为 "RYXSTDV"
        ma_value_column: 移动平均值列名，默认为 "MA_RYX"
        ma_stdv_column: 移动平均标准差列名，默认为 "MA_RYXSTDV"
        
    Returns:
        包含移动平均的DataFrame
    """
    if df is None or df.empty:
        return None

    # 确保日期列是datetime类型
    df[date_column] = pd.to_datetime(df[date_column])

    # 设置日期列为索引，以便按日期计算移动平均
    df_indexed = df.set_index(date_column)

    # 计算移动平均，使用指定的窗口大小（天数）
    df_ma = df_indexed.rolling(f'{window_days}D').mean().reset_index()

    # 添加移动平均列标识
    df_ma[ma_value_column] = df_ma[value_column]
    df_ma[ma_stdv_column] = df_ma[stdv_column]

    # 合并原始数据和移动平均数据
    result = pd.merge(df,
                      df_ma[[date_column, ma_value_column, ma_stdv_column]],
                      on=date_column,
                      how='left')

    return result


def plot_data(
        data_dict: Dict[int, pd.DataFrame],
        window_days: int,
        station_id: str = "",
        point_id: str = "",
        station_name: str = "监测站",  # 添加站点名称参数，默认为"监测站"
        output_filename: Optional[str] = None,
        show_plot: bool = False,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        # 添加列名参数
        date_column: str = "STARTDATE",
        value_column: str = "RYX",
        stdv_column: str = "RYXSTDV",
        ma_value_column: str = "MA_RYX") -> str:
    """绘制数据图表
    
    Args:
        data_dict: 包含不同频率数据的字典，格式为 {frequency: dataframe}
        window_days: 移动平均窗口大小（天数）
        station_id: 站点ID（用于标题和文件名）
        point_id: 点位ID（用于标题和文件名）
        station_name: 站点名称（用于标题显示），默认为"监测站"
        output_filename: 输出文件名，如果为None则自动生成
        show_plot: 是否显示图表
        period_start: 特定时间段的开始日期（用于计算均值），格式为 "YYYY-MM-DD"
        period_end: 特定时间段的结束日期（用于计算均值），格式为 "YYYY-MM-DD"
        date_column: 日期列名，默认为 "STARTDATE"
        value_column: 值列名，默认为 "RYX"
        stdv_column: 标准差列名，默认为 "RYXSTDV"
        ma_value_column: 移动平均值列名，默认为 "MA_RYX"
        
    Returns:
        保存的图表文件路径
    """
    if not data_dict or all(df is None or df.empty
                            for df in data_dict.values()):
        print("No data available for plotting")
        return ""

    # 设置绘图样式
    set_plot_style()

    # 获取频率列表
    frequencies = list(data_dict.keys())

    # 创建一个大画布，包含两个子图
    fig, axes = plt.subplots(len(frequencies),
                             1,
                             figsize=(10, 5 * len(frequencies)),
                             sharex=True)
    fig.subplots_adjust(hspace=0.1)  # 减少垂直间距

    # 如果只有一个频率，确保axes是列表
    if len(frequencies) == 1:
        axes = [axes]

    # 设置颜色周期和标记样式
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    markers = ['o', 's', '^', 'D', 'v', 'p']

    # 为每个频率绘制数据
    for i, (freq, df) in enumerate(data_dict.items()):
        if df is not None and not df.empty:
            ax = axes[i]

            # 绘制原始数据点
            ax.errorbar(df[date_column],
                        df[value_column],
                        yerr=df[stdv_column],
                        fmt=markers[i % len(markers)],
                        color=colors[i % len(colors)],
                        markersize=4,
                        markeredgecolor='black',
                        markeredgewidth=0.5,
                        capsize=2,
                        elinewidth=0.8,
                        capthick=0.8,
                        alpha=0.3,
                        label=f'{freq} Hz Data')

            # 绘制移动平均线
            if ma_value_column in df.columns and not df[ma_value_column].isna(
            ).all():
                ax.plot(df[date_column],
                        df[ma_value_column],
                        color=colors[i % len(colors)],
                        linewidth=2.5,
                        alpha=0.9,
                        label=f'{freq} Hz {window_days}-day MA')

            # 计算特定时间段内的均值
            if period_start and period_end:
                period_start_ts = pd.Timestamp(period_start)
                period_end_ts = pd.Timestamp(period_end)
                period_data = df[(df[date_column] >= period_start_ts)
                                 & (df[date_column] <= period_end_ts)]

                if not period_data.empty:
                    period_mean = period_data[value_column].mean()

                    # 绘制均值线
                    ax.axhline(
                        y=period_mean,
                        color='red',
                        linestyle='--',
                        linewidth=2,
                        label=
                        f'{period_start} to {period_end} Mean: {period_mean:.2f} Ω·m'
                    )

                    # 添加文本标注
                    ax.text(df[date_column].max() - pd.Timedelta(days=30),
                            period_mean * 1.05,
                            f'Mean: {period_mean:.2f} Ω·m',
                            color='red',
                            fontsize=12,
                            fontweight='bold')

            # 设置y轴为线性坐标
            ax.set_yscale('linear')

            # 设置标题和标签
            if i == 0:  # 顶部子图
                if station_id and point_id:
                    ax.set_title(
                        f'{station_name}极低频视电阻率（{station_id}_{point_id}）',
                        fontsize=20,
                        fontweight='bold',
                        pad=15)
                else:
                    ax.set_title(f'{station_name}极低频视电阻率',
                                 fontsize=20,
                                 fontweight='bold',
                                 pad=15)

            # 设置y轴标签
            ax.set_ylabel('Apparent Resistivity (Ω·m)',
                          fontsize=16,
                          fontweight='bold')

            # 添加网格
            ax.grid(True,
                    which='both',
                    linestyle='--',
                    linewidth=0.5,
                    alpha=0.7)

            # 添加图例
            ax.legend(loc='upper right',
                      frameon=True,
                      fontsize=14,
                      fancybox=False)

    # 设置适当的y轴范围
    for i, ax in enumerate(axes):
        if i < len(frequencies) and data_dict.get(frequencies[i]) is not None:
            df = data_dict[frequencies[i]]
            if not df.empty:
                min_val = df[value_column].min() * 0.9  # 留出一些空间
                max_val = df[value_column].max() * 1.1
                ax.set_ylim(min_val, max_val)

    # 设置x轴格式
    for ax in axes:
        # 设置主要日期刻度
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        # 设置次要日期刻度
        ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=1))

    # 给最底部的子图添加x轴标签
    axes[-1].set_xlabel('Observation Time', fontsize=16, fontweight='bold')

    # 旋转x轴刻度标签以防止重叠
    fig.autofmt_xdate()

    # 添加总标题
    fig.suptitle(
        f'Magnetotelluric Apparent Resistivity ({window_days}-day Moving Average)',
        fontsize=22,
        fontweight='bold',
        y=0.98)

    # 调整布局
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # 生成输出文件名
    if output_filename is None:
        freq_str = "_".join([f"{f}Hz" for f in frequencies])
        if station_id and point_id:
            output_filename = f"MT_Rho_{station_id}_{point_id}_{freq_str}_{window_days}day_avg.png"
        else:
            output_filename = f"MT_Rho_{freq_str}_{window_days}day_avg.png"

    # 保存为高分辨率PNG图片
    plt.savefig(output_filename, dpi=600, bbox_inches='tight', pad_inches=0.3)
    print(f"图表已保存为: {os.path.abspath(output_filename)}")

    # 显示图表
    if show_plot:
        plt.show()
    else:
        plt.close(fig)

    return os.path.abspath(output_filename)


def process_and_plot_mt_data(
        start_time: str,
        end_time: str,
        station_id: str,
        point_id: str,
        frequencies: List[int],
        moving_avg_days: int = 5,
        db_connection: Optional[Union[cx_Oracle.Connection, str]] = None,
        oracle_client_lib: Optional[str] = None,
        output_filename: Optional[str] = None,
        show_plot: bool = False,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        station_name: str = "监测站",  # 添加站点名称参数，默认为"监测站"
        verbose: bool = True,
        # 添加表名和列名配置参数
        table_name: str = "QZDATA.QZ_CP_372_90_AVG",
        date_column: str = "STARTDATE",
        value_column: str = "RYX",
        stdv_column: str = "RYXSTDV",
        station_column: str = "STATIONID",
        point_column: str = "POINTID",
        freq_column: str = "FREQUENCIES",
        # 添加移动平均列名参数
        ma_value_column: str = "MA_RYX",
        ma_stdv_column: str = "MA_RYXSTDV") -> str:
    """处理并绘制极低频视电阻率数据的主函数
    
    Args:
        start_time: 开始时间，格式为 "YYYY-MM-DD HH:MM:SS"
        end_time: 结束时间，格式为 "YYYY-MM-DD HH:MM:SS"
        station_id: 站点ID
        point_id: 点位ID
        frequencies: 频率列表(Hz)
        moving_avg_days: 移动平均窗口大小（天数）
        db_connection: 数据库连接对象或连接名称
        oracle_client_lib: Oracle客户端库目录路径
        output_filename: 输出文件名，如果为None则自动生成
        show_plot: 是否显示图表
        period_start: 特定时间段的开始日期（用于计算均值），格式为 "YYYY-MM-DD"
        period_end: 特定时间段的结束日期（用于计算均值），格式为 "YYYY-MM-DD"
        station_name: 站点名称（用于标题显示），默认为"监测站"
        verbose: 是否输出处理信息
        table_name: 数据表名，默认为 "QZDATA.QZ_CP_372_90_AVG"
        date_column: 日期列名，默认为 "STARTDATE"
        value_column: 值列名，默认为 "RYX"
        stdv_column: 标准差列名，默认为 "RYXSTDV"
        station_column: 站点ID列名，默认为 "STATIONID"
        point_column: 点位ID列名，默认为 "POINTID"
        freq_column: 频率列名，默认为 "FREQUENCIES"
        ma_value_column: 移动平均值列名，默认为 "MA_RYX"
        ma_stdv_column: 移动平均标准差列名，默认为 "MA_RYXSTDV"
        
    Returns:
        保存的图表文件路径
    """
    if verbose:
        print(f"正在查询数据... (时间范围: {start_time} 至 {end_time})")
        print(f"设置移动平均窗口: {moving_avg_days} 天")

    # 初始化Oracle客户端（如果提供了路径）
    if oracle_client_lib:
        init_oracle_client(lib_dir=oracle_client_lib)

    # 存储不同频率的数据
    data_dict = {}

    # 查询每个频率的数据
    for frequency in frequencies:
        if verbose:
            print(f"查询频率 {frequency}Hz 的数据...")

        df = query_data(start_time, end_time, station_id, point_id, frequency,
                        db_connection, table_name, date_column, value_column,
                        stdv_column, station_column, point_column, freq_column)

        if df is not None and not df.empty:
            if verbose:
                print(f"查询到 {len(df)} 条 {frequency}Hz 频率的记录")

            # 数据预处理：根据频率过滤数据
            if verbose:
                print(f"对 {frequency}Hz 数据进行预处理...")

            df = preprocess_data(df, frequency, value_column, verbose=verbose)

            if verbose:
                print(f"预处理后剩余 {len(df)} 条 {frequency}Hz 频率的记录")
                if len(df) > 0:
                    print("前5条数据示例:")
                    print(df.head())

            # 计算移动平均
            if verbose:
                print(f"计算 {moving_avg_days} 天移动平均...")

            df_with_ma = calculate_moving_average(df, moving_avg_days,
                                                  date_column, value_column,
                                                  stdv_column, ma_value_column,
                                                  ma_stdv_column)
            data_dict[frequency] = df_with_ma

            if verbose and df_with_ma is not None and not df_with_ma.empty:
                print(f"{frequency}Hz 移动平均后的数据示例:")
                print(df_with_ma[[date_column, value_column,
                                  ma_value_column]].head())
        else:
            if verbose:
                print(f"未能获取 {frequency}Hz 频率的数据")

    # 检查是否成功获取了任何数据
    if any(df is not None and not df.empty for df in data_dict.values()):
        if verbose:
            print("正在绘制图表...")

        filepath = plot_data(
            data_dict,
            moving_avg_days,
            station_id,
            point_id,
            station_name,  # 传递站点名称参数
            output_filename,
            show_plot,
            period_start,
            period_end,
            date_column,
            value_column,
            stdv_column,
            ma_value_column)
        return filepath
    else:
        if verbose:
            print("未能获取任何数据，请检查连接参数和查询条件")
        return ""
