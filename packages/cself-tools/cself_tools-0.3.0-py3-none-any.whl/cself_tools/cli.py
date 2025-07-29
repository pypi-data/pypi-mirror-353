import argparse
import sys
from .mt_resistivity import process_and_plot_mt_data


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description='极低频视电阻率数据处理工具')

    # 基本查询参数
    parser.add_argument('--start-time',
                        type=str,
                        default="2020-01-01 00:00:00",
                        help='查询开始时间 (默认: 2020-01-01 00:00:00)')

    parser.add_argument('--end-time',
                        type=str,
                        default="2025-05-31 23:59:59",
                        help='查询结束时间 (默认: 2025-05-31 23:59:59)')

    parser.add_argument('--station-id',
                        type=str,
                        default="37024",
                        help='站点ID (默认: 37024)')

    parser.add_argument('--point-id',
                        type=str,
                        default="E",
                        help='点位ID (默认: E)')

    parser.add_argument('--station-name',
                        type=str,
                        default="监测站",
                        help='站点名称 (默认: 监测站)')

    parser.add_argument('--frequencies',
                        type=int,
                        nargs='+',
                        default=[22, 74],
                        help='频率列表，以空格分隔 (默认: 22 74)')

    parser.add_argument('--moving-avg-days',
                        type=int,
                        default=5,
                        help='移动平均窗口大小（天数） (默认: 5)')

    # 数据库连接参数
    parser.add_argument('--db-connection',
                        type=str,
                        default="DB-Shandong-12",
                        help='数据库连接名称 (默认: DB-Shandong-12)')

    parser.add_argument('--oracle-client-lib',
                        type=str,
                        default="C:/instantclient",
                        help='Oracle客户端库目录路径 (默认: C:/instantclient)')

    # 表结构配置参数
    parser.add_argument('--table-name',
                        type=str,
                        default="QZDATA.QZ_CP_372_90_AVG",
                        help='数据表名 (默认: QZDATA.QZ_CP_372_90_AVG)')

    parser.add_argument('--date-column',
                        type=str,
                        default="STARTDATE",
                        help='日期列名 (默认: STARTDATE)')

    parser.add_argument('--value-column',
                        type=str,
                        default="RYX",
                        help='值列名 (默认: RYX)')

    parser.add_argument('--stdv-column',
                        type=str,
                        default="RYXSTDV",
                        help='标准差列名 (默认: RYXSTDV)')

    parser.add_argument('--station-column',
                        type=str,
                        default="STATIONID",
                        help='站点ID列名 (默认: STATIONID)')

    parser.add_argument('--point-column',
                        type=str,
                        default="POINTID",
                        help='点位ID列名 (默认: POINTID)')

    parser.add_argument('--freq-column',
                        type=str,
                        default="FREQUENCIES",
                        help='频率列名 (默认: FREQUENCIES)')

    parser.add_argument('--ma-value-column',
                        type=str,
                        default="MA_RYX",
                        help='移动平均值列名 (默认: MA_RYX)')

    parser.add_argument('--ma-stdv-column',
                        type=str,
                        default="MA_RYXSTDV",
                        help='移动平均标准差列名 (默认: MA_RYXSTDV)')

    # 输出和显示参数
    parser.add_argument('--output-filename', type=str, help='输出文件名 (默认: 自动生成)')

    parser.add_argument('--show-plot',
                        action='store_true',
                        help='显示图表 (默认: 不显示)')

    parser.add_argument('--period-start',
                        type=str,
                        help='特定时间段的开始日期，用于计算均值 (格式: YYYY-MM-DD)')

    parser.add_argument('--period-end',
                        type=str,
                        help='特定时间段的结束日期，用于计算均值 (格式: YYYY-MM-DD)')

    parser.add_argument('--quiet', action='store_true', help='静默模式，不输出处理信息')

    args = parser.parse_args()

    # 处理并绘制数据
    try:
        filepath = process_and_plot_mt_data(
            start_time=args.start_time,
            end_time=args.end_time,
            station_id=args.station_id,
            point_id=args.point_id,
            frequencies=args.frequencies,
            moving_avg_days=args.moving_avg_days,
            db_connection=args.db_connection,
            oracle_client_lib=args.oracle_client_lib,
            output_filename=args.output_filename,
            show_plot=args.show_plot,
            period_start=args.period_start,
            period_end=args.period_end,
            station_name=args.station_name,
            verbose=not args.quiet,
            # 表结构配置参数
            table_name=args.table_name,
            date_column=args.date_column,
            value_column=args.value_column,
            stdv_column=args.stdv_column,
            station_column=args.station_column,
            point_column=args.point_column,
            freq_column=args.freq_column,
            ma_value_column=args.ma_value_column,
            ma_stdv_column=args.ma_stdv_column)

        if filepath:
            if not args.quiet:
                print(f"\n成功: 图表已保存到 {filepath}")
            return 0
        else:
            print("\n错误: 处理失败，无法生成图表")
            return 1

    except Exception as e:
        print(f"\n错误: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
