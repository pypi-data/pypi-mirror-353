"""
lunar_calendar_core.py

此模块包含了农历日历的核心计算逻辑，包括查找农历月份索引、
寻找冬至月合朔日以及生成农历月序表和合朔儒略日列表。
"""

import ephem
from typing import List, Tuple
from .constants import YUEFEN
from .julian_date_utils import jd_to_date, is_date_greater_or_equal
from .solar_terms import calculate_solar_term_jd

def find_lunar_month_index(julian_date: float, new_moon_jds: List[float]) -> int:
    """
    查找给定儒略日所在的农历月份索引。

    Args:
        julian_date (float): 需要查找的儒略日（UT 时间）。
        new_moon_jds (List[float]): 合朔儒略日列表，从冬至月合朔开始。

    Returns:
        int: 儒略日所在的农历月序（从0开始计数，0代表冬至月）。
    """
    lunar_month_index = -1
    for jd_new_moon in new_moon_jds:
        if is_date_greater_or_equal(julian_date, jd_new_moon):
            lunar_month_index += 1
        else:
            break
    return lunar_month_index

def find_winter_solstice_new_moon(year: int) -> ephem.Date:
    """
    寻找指定年份前冬至月合朔日。

    Args:
        year (int): 公历年份。

    Returns:
        ephem.Date: 冬至月合朔的 ephem.Date 对象。
    """
    # 处理公元1年的特殊情况，公元元年前冬至在公元前1年
    if year == 1:
        year -= 1

    # 获取指定年份前一年的冬至日期
    winter_solstice = ephem.next_solstice((year - 1, 12))
    winter_solstice_jd = ephem.julian_date(winter_solstice)

    # 寻找冬至前后的合朔日，可能在冬至当月、前一月或前两月
    # 尝试三个可能的朔日，以确保找到正确的冬至月合朔
    new_moon_candidate1 = ephem.next_new_moon(jd_to_date(winter_solstice_jd))
    new_moon_candidate1_jd = ephem.julian_date(new_moon_candidate1)

    new_moon_candidate2 = ephem.next_new_moon(jd_to_date(winter_solstice_jd - 29))
    new_moon_candidate2_jd = ephem.julian_date(new_moon_candidate2)

    new_moon_candidate3 = ephem.next_new_moon(jd_to_date(winter_solstice_jd - 31))
    new_moon_candidate3_jd = ephem.julian_date(new_moon_candidate3)

    # 判断哪个合朔日是冬至月合朔
    if is_date_greater_or_equal(winter_solstice_jd, new_moon_candidate1_jd):
        # 冬至合朔在同一日或下月
        return new_moon_candidate1
    elif is_date_greater_or_equal(winter_solstice_jd, new_moon_candidate2_jd) and \
         not is_date_greater_or_equal(winter_solstice_jd, new_moon_candidate1_jd):
        return new_moon_candidate2
    elif is_date_greater_or_equal(winter_solstice_jd, new_moon_candidate3_jd):
        # 冬至在上月
        return new_moon_candidate3
    else:
        # 理论上不会发生，但为了健壮性
        raise ValueError("无法找到冬至月合朔日。")


def generate_lunar_calendar_data(year: int, include_next_year_winter_solstice_month: bool = True) -> Tuple[List[str], List[float]]:
    """
    生成指定年份的农历月序表和合朔儒略日列表。

    Args:
        year (int): 公历年份。
        include_next_year_winter_solstice_month (bool):
            如果为 True，则计算到次年冬至朔；如果为 False，则计算到次年冬至朔的次月。
            这影响了闰月的判断和月序的生成。

    Returns:
        Tuple[List[str], List[float]]:
            - List[str]: 农历月名表。
            - List[float]: 合朔儒略日列表（UT 时间），从冬至月合朔开始。
    """
    # 寻找本年冬至月合朔日
    winter_solstice_new_moon = find_winter_solstice_new_moon(year)
    current_new_moon = winter_solstice_new_moon  # 用于迭代计算下一个朔日
    new_moon_jds = [ephem.julian_date(winter_solstice_new_moon)]  # 存储合朔儒略日

    # 寻找次年冬至月合朔日
    next_winter_solstice_new_moon_jd = ephem.julian_date(find_winter_solstice_new_moon(year + 1))

    middle_qi_index = -1  # 中气序，从0起计（冬至为0）
    new_moon_count = -1  # 计算连续两个冬至月中的合朔次数，从0起计
    leap_month_index = 0  # 闰月索引，如果存在
    has_found_leap_month = False  # 标记是否已找到闰月

    # 查找所在月及判断置闰
    # 循环直到达到次年冬至朔（或次年冬至朔的次月）
    while not is_date_greater_or_equal(new_moon_jds[new_moon_count + include_next_year_winter_solstice_month], next_winter_solstice_new_moon_jd):
        middle_qi_index += 1
        new_moon_count += 1
        current_new_moon = ephem.next_new_moon(current_new_moon)  # 计算次月朔
        new_moon_jds.append(ephem.julian_date(current_new_moon))

        # 冬至月一定含中气，从次月开始查找是否置闰
        if new_moon_count == 0:
            continue

        # 本月应含的中气角度（冬至为-90度，每月中气增加30度）
        expected_middle_qi_angle = (-90 + 30 * middle_qi_index) % 360
        # 计算本月应含中气的儒略日
        middle_qi_jd = calculate_solar_term_jd(year, expected_middle_qi_angle)

        # 判断本月是否无中气，若无则置闰
        # 如果中气在次月合朔之后，则本月无中气
        if is_date_greater_or_equal(middle_qi_jd, new_moon_jds[new_moon_count + 1]) and not has_found_leap_month:
            leap_month_index = new_moon_count + 1  # 记录闰月的位置
            middle_qi_index -= 1  # 因为置闰，中气序不增加
            has_found_leap_month = True  # 仅第一个无中气月置闰

    # 生成农历月序表
    lunar_month_names = []
    for k in range(len(new_moon_jds)):
        # 默认月序：冬至月为十一月，所以 (k - 2) % 12 对应正月、二月...
        lunar_month_names.append(YUEFEN[(k - 2) % 12])

        # 如果存在闰月，并且当前合朔次数为12次（即有闰月），则修改月名
        # new_moon_count + include_next_year_winter_solstice_month 实际上是总的合朔月数
        if new_moon_count + include_next_year_winter_solstice_month == 13:
            if k + 1 == leap_month_index:
                # 闰月名称为前一个月的闰月
                lunar_month_names[k] = '闰' + YUEFEN[(k - 1 - 2) % 12]
            elif k + 1 > leap_month_index:
                # 闰月之后的月份，月序减一
                lunar_month_names[k] = YUEFEN[(k - 1 - 2) % 12]

    return lunar_month_names, new_moon_jds
