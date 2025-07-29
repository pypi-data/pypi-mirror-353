"""
julian_date_utils.py

此模块提供了儒略日（Julian Date）与 `ephem.Date` 对象之间的转换，
以及日期比较和差异计算的实用函数。
"""

import ephem
import math

def jd_to_date(julian_date: float, ut_offset: float = 0) -> ephem.Date:
    """
    将儒略日转换为 ephem.Date 对象。

    Args:
        julian_date (float): 儒略日。
        ut_offset (float): UTC 偏移量，单位为小时。默认为 0。

    Returns:
        ephem.Date: 对应的 ephem.Date 对象。
    """
    # ephem.Date 的基准儒略日是 2415020.0 (1899年12月31日 12:00 UT)
    return ephem.Date(julian_date + ut_offset / 24 - 2415020)

def get_date_difference(jd1: float, jd2: float) -> int:
    """
    计算两个儒略日（考虑 UTC+8 时区）之间的天数差。

    Args:
        jd1 (float): 第一个儒略日。
        jd2 (float): 第二个儒略日。

    Returns:
        int: 天数差。
    """
    # 儒略日转换为北京时间（UTC+8）的日期，然后取整计算天数差
    return math.floor(jd1 + 8 / 24 + 0.5) - math.floor(jd2 + 8 / 24 + 0.5)

def is_date_greater_or_equal(jd1: float, jd2: float) -> bool:
    """
    比较两个儒略日（考虑 UTC+8 时区），判断 jd1 是否大于或等于 jd2。

    Args:
        jd1 (float): 第一个儒略日。
        jd2 (float): 第二个儒略日。

    Returns:
        bool: 如果 jd1 大于或等于 jd2，则返回 True；否则返回 False。
    """
    return get_date_difference(jd1, jd2) >= 0
