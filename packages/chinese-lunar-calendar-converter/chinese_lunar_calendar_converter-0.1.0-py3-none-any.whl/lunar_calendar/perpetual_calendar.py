"""
perpetual_calendar.py

此模块提供了打印农历和公历对照万年历的功能。
"""

import ephem
from typing import List
from .constants import NLRQ, YUEFEN
from .julian_date_utils import jd_to_date, get_date_difference, is_date_greater_or_equal
from .lunar_calendar_core import find_lunar_month_index, generate_lunar_calendar_data

def print_perpetual_calendar(year: int, month: int = 0) -> None:
    """
    打印指定年份（或月份）的万年历（农历及公历对照）。

    Args:
        year (int): 公历年份。
        month (int, optional): 公历月份 (1-12)。如果为 0，则输出全年日历。默认为 0。

    Raises:
        ValueError: 如果年份为 0。
    """
    if year == 0:
        raise ValueError("不存在公元0年")

    # 生成农历月序表和合朔儒略日列表
    # 这里使用 generate_lunar_calendar_data(year, 0) 对应原始代码的 type=0，即截止到次年冬至朔次月
    lunar_month_names, new_moon_jds = generate_lunar_calendar_data(year, include_next_year_winter_solstice_month=False)

    # 检查是否需要扩展农历数据到次年，以覆盖公历年末
    # 原始代码的逻辑是检查公历12月31日是否在倒数第二个朔日+29天之后
    # 如果是，则需要从次年获取农历数据来补充
    dec_31_jd = ephem.julian_date((year, 12, 31))
    if is_date_greater_or_equal(dec_31_jd, new_moon_jds[-2] + 29):
        # 获取次年的农历数据，只取前两个月（冬至月和次月）
        next_year_lunar_month_names, next_year_new_moon_jds = generate_lunar_calendar_data(year + 1, include_next_year_winter_solstice_month=True)
        lunar_month_names = lunar_month_names[:-2] + next_year_lunar_month_names[:2]
        new_moon_jds = new_moon_jds[:-2] + next_year_new_moon_jds[:3]

    # 计算每月天数
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    # 判断闰年
    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
        days_in_month[1] = 29
    # 儒略历的闰年规则 (1582年之前)
    if year < 1582 and year % 4 == 0:
        days_in_month[1] = 29

    # 星期名称
    week_names = ['一', '二', '三', '四', '五', '六', '日']

    for j in range(12): # 遍历12个月
        if month != 0 and j + 1 != month: # 如果指定了月份，则跳过其他月份
            continue

        print(f'【{year}年 {j + 1}月  日历】')

        # 获取当前公历月份第一天的儒略日
        first_day_of_month_jd = ephem.julian_date((year, j + 1))
        # 查找公历月份第一天对应的农历月份索引
        lunar_month_start_index = find_lunar_month_index(first_day_of_month_jd, new_moon_jds)
        # 计算公历月份第一天在农历月内的日期（初几）
        lunar_day_of_month_start = get_date_difference(first_day_of_month_jd, new_moon_jds[lunar_month_start_index])

        # 计算当月第一天是星期几 (0=星期日, 1=星期一...)
        # ephem.julian_date((year, j + 1)) + 0.5 是为了四舍五入到最近的午夜，然后 % 7 得到星期几
        # 0.5 是因为 ephem.Date 是 UT 时间，需要转换为本地时间（UTC+8）并考虑儒略日从中午开始
        # 原始代码是 int((ysJD + 0.5) % 7)，这里 ysJD 已经是 ephem.julian_date((year, j + 1))
        # 儒略日是从中午开始的，所以 +0.5 使得日期从午夜开始计算星期几
        first_day_weekday_index = int((first_day_of_month_jd + 0.5) % 7)

        # 打印星期头
        for k in range(7):
            print(f" {week_names[k]:<5}", end='')
        print()

        # 打印日历内容
        current_day_of_month = 1
        calendar_finished = False
        for row in range(6): # 最多6行，每行7天
            if calendar_finished:
                break
            
            # 打印公历日期行
            for k in range(7):
                if row == 0 and k < first_day_weekday_index:
                    print('       ', end='') # 打印空白填充
                else:
                    if current_day_of_month <= days_in_month[j]:
                        # 处理1582年10月的特殊情况（格里高利历改革）
                        display_day = current_day_of_month
                        if year == 1582 and j == 9: # 10月 (j=9)
                            if current_day_of_month > 4: # 10月4日之后跳过10天
                                display_day += 10
                        print(f" {display_day:<6d}", end='')
                        current_day_of_month += 1
                    else:
                        calendar_finished = True
                        break
            print() # 换行

            if calendar_finished:
                break

            # 打印农历日期行
            for k in range(7):
                if row == 0 and k < first_day_weekday_index:
                    print('       ', end='') # 打印空白填充
                else:
                    # 计算当前格子的农历日期索引
                    # 原始代码的 rqx = ysRQ + row // 2 * 7 - 7 + k - blank
                    # 这里的 ysRQ 是 lunar_day_of_month_start
                    # blank 是 first_day_weekday_index
                    # row // 2 * 7 - 7 + k 是当前格子相对于第一天（索引0）的偏移量
                    # 简化为：当前格子是公历月份的第几天
                    day_in_month_for_lunar = (row * 7 + k) - first_day_weekday_index + 1
                    if day_in_month_for_lunar > days_in_month[j]:
                        if year == 1582 and j == 9 and day_in_month_for_lunar > days_in_month[j]:
                            # 1582年10月特殊处理，跳过10天后，如果超出当月天数则停止
                            pass
                        else:
                            break # 超出当月天数，停止打印农历
                    
                    # 计算当前格子对应的儒略日
                    current_cell_jd = ephem.julian_date((year, j + 1, day_in_month_for_lunar)) - 8 / 24
                    
                    # 查找当前格子所在的农历月份索引
                    current_lunar_month_index = find_lunar_month_index(current_cell_jd, new_moon_jds)
                    # 计算当前格子在农历月内的日期（初几）
                    current_lunar_day_index = get_date_difference(current_cell_jd, new_moon_jds[current_lunar_month_index])

                    # 获取农历月名和日名
                    lunar_month_name = lunar_month_names[current_lunar_month_index]
                    lunar_day_name = NLRQ[current_lunar_day_index]

                    # 打印农历日期
                    print(f"{lunar_month_name}{lunar_day_name:<3}", end=' ')
            print() # 换行
        print() # 额外空行
