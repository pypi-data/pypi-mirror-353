"""
solar_terms.py

此模块提供了计算二十四节气相关的功能，包括二分二至点的儒略日计算、
太阳黄经的获取以及节气儒略日的精确计算。
"""

import ephem
import math
from .julian_date_utils import jd_to_date

def get_equinox_solstice_jd(year: int, angle: float) -> float:
    """
    计算指定年份和角度的二分二至点儒略日。

    Args:
        year (int): 公历年份。
        angle (float): 太阳黄经角度（0, 90, 180, 270 分别对应春分、夏至、秋分、冬至）。

    Returns:
        float: 对应的儒略日。
    """
    if 0 <= angle < 90:
        date = ephem.next_vernal_equinox(str(year))
    elif 90 <= angle < 180:
        date = ephem.next_summer_solstice(str(year))
    elif 180 <= angle < 270:
        date = ephem.next_autumn_equinox(str(year))
    else: # 270 <= angle < 360
        date = ephem.next_winter_solstice(str(year))
    return ephem.julian_date(date)

def get_solar_longitude(julian_date: float) -> float:
    """
    计算指定儒略日（UT 时间）的太阳黄经。

    Args:
        julian_date (float): 儒略日（UT 时间）。

    Returns:
        float: 太阳黄经，单位为弧度。
    """
    date = jd_to_date(julian_date)  # date应为UT时间
    s = ephem.Sun(date)
    sa = ephem.Equatorial(s.ra, s.dec, epoch=date)
    se = ephem.Ecliptic(sa)
    return se.lon

def calculate_solar_term_jd(year: int, angle: float) -> float:
    """
    精确计算指定年份和角度的节气儒略日（UT 时间）。

    Args:
        year (int): 公历年份。
        angle (float): 节气对应的太阳黄经角度（0-360度）。

    Returns:
        float: 节气对应的儒略日（UT 时间）。
    """
    # 如果角度大于270度（冬至），则年份减1，因为农历年通常从冬至开始计算
    if angle > 270:
        year -= 1
    # 处理公元0年的情况，ephem库不识别公元0年，将其转换为公元前1年
    if year == 0:
        year -= 1

    # 获取节气的初始儒略日估算值
    initial_jd = get_equinox_solstice_jd(year, angle)

    # 对于冬至（angle >= 270），需要检查是否是年末冬至，如果不是则转入次年
    if angle >= 270:
        # 计算前一个节气（例如，冬至的前一个节气是秋分）的儒略日
        jd_prev_quarter = get_equinox_solstice_jd(year, (angle - 90) % 360)
        # 如果当前节气（冬至）的儒略日小于前一个节气的儒略日，说明是次年的冬至
        if initial_jd < jd_prev_quarter:
            initial_jd = get_equinox_solstice_jd(year + 1, angle)

    jd1 = initial_jd
    # 迭代逼近精确的节气儒略日
    while True:
        jd2 = jd1
        # 获取当前儒略日对应的太阳黄经（弧度）
        solar_longitude = get_solar_longitude(jd2)
        # 根据黄经差值调整儒略日，使其更接近目标角度
        jd1 += math.sin(math.radians(angle) - solar_longitude) / math.pi * 180
        # 当儒略日的变化小于0.00001（约1秒）时，认为达到足够精度
        if abs(jd1 - jd2) < 0.00001:
            break
    return jd1  # 返回UT时间
