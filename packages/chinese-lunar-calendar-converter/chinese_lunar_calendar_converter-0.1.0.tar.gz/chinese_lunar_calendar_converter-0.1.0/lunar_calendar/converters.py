import ephem
import math
from typing import Tuple, Any
from .constants import YUEFEN, NLRQ, GANZHI_CYCLE
from .julian_date_utils import jd_to_date, get_date_difference, is_date_greater_or_equal
from .solar_terms import calculate_solar_term_jd
from .lunar_calendar_core import find_lunar_month_index, find_winter_solstice_new_moon, generate_lunar_calendar_data

def solar_to_lunar(gregorian_date_str: str) -> Tuple[str, str, str, str, str]:
    # 将公历日期转换为儒略日
    try:
        jd_ut = ephem.julian_date(ephem.Date(gregorian_date_str)) - 8 / 24
    except Exception as e:
        raise ValueError(f"无效的公历日期格式或日期值: {gregorian_date_str}. 错误: {e}")

    # 将儒略日转换为公历日期
    year, month, day = jd_to_date(jd_ut, 8).triple()
    year, month, day = int(year), int(month), int(day)

    # 判断是否存在公元0年
    if year == 0:
        raise ValueError("不存在公元0年")

    # 找到本年的冬至朔日
    this_winter_solstice_new_moon_jd = ephem.julian_date(find_winter_solstice_new_moon(year))
    # 找到下年的冬至朔日
    next_winter_solstice_new_moon_jd = ephem.julian_date(find_winter_solstice_new_moon(year + 1))

    # 判断农历年份
    lunar_year = year
    if is_date_greater_or_equal(jd_ut, next_winter_solstice_new_moon_jd):
        lunar_year += 1
    elif not is_date_greater_or_equal(jd_ut, this_winter_solstice_new_moon_jd):
        lunar_year -= 1

    # 生成农历数据
    lunar_month_names, new_moon_jds = generate_lunar_calendar_data(lunar_year)
    # 找到农历月份索引
    lunar_month_index = find_lunar_month_index(jd_ut, new_moon_jds)

    # 计算干支年份
    solar_year_for_ganzhi = year
    if solar_year_for_ganzhi < 0:
        solar_year_for_ganzhi += 1

    # 计算节气儒略日
    jqy, jqr = jd_to_date(calculate_solar_term_jd(year, month * 30 + 255), 8).triple()[1:]
    # 判断节气儒略日是否与月份相同
    if int(jqy) != month:
        month -= (int(jqy) - month)
    # 判断日期是否大于节气儒略日
    if day >= int(jqr):
        lunar_month_ganzhi = GANZHI_CYCLE[(solar_year_for_ganzhi * 12 + 12 + month) % 60]
    else:
        lunar_month_ganzhi = GANZHI_CYCLE[(solar_year_for_ganzhi * 12 + 11 + month) % 60]

    # 判断农历月份索引是否小于3
    if lunar_month_index < 3:
        lunar_year -= 1
    # 判断农历年份是否小于0
    if lunar_year < 0:
        lunar_year += 1
    # 计算干支年份
    lunar_year_ganzhi = GANZHI_CYCLE[(lunar_year - 4) % 60]

    # 计算干支日期
    lunar_day_ganzhi = GANZHI_CYCLE[math.floor(jd_ut + 8 / 24 + 0.5 + 49) % 60]
    
    # 计算日期差
    lunar_day_index = get_date_difference(jd_ut, new_moon_jds[lunar_month_index])

    # 返回农历年份、月份、日期、月份名称、农历日期
    return (
        lunar_year_ganzhi,
        lunar_month_ganzhi,
        lunar_day_ganzhi,
        lunar_month_names[lunar_month_index],
        NLRQ[lunar_day_index]
    )


def lunar_to_solar(lunar_year: int, lunar_date_str: str) -> Tuple[int, int, int]:
    # 判断是否存在公元0年
    if lunar_year == 0:
        raise ValueError("不存在公元0年")

    # 判断是否为闰月
    is_leap_month = "闰" in lunar_date_str
    # 去除闰字
    clean_lunar_date_str = lunar_date_str.replace("闰", "")
    
    # 获取农历月份名称
    lunar_month_name = clean_lunar_date_str[:-2]
    # 获取农历日期名称
    lunar_day_name = clean_lunar_date_str[-2:]

    # 判断农历月份名称是否有效
    try:
        month_index_in_yuefen = YUEFEN.index(lunar_month_name)
    except ValueError:
        raise ValueError(f"无效的农历月份名称: {lunar_month_name}")

    # 获取农历数据的目标年份
    target_year_for_lunar_data = lunar_year
    if month_index_in_yuefen + 1 > 10:
        target_year_for_lunar_data += 1

    # 生成农历数据
    lunar_month_names, new_moon_jds = generate_lunar_calendar_data(target_year_for_lunar_data, include_next_year_winter_solstice_month=False)

    # 初始化变量
    szy = 0
    found_month = False
    # 遍历农历月份名称
    for i in range(len(lunar_month_names)):
        # 判断是否为闰月
        if lunar_month_names[i] == lunar_month_name:
            if is_leap_month:
                # 判断前一个月是否为闰月
                if i > 0 and lunar_month_names[i-1] == '闰' + lunar_month_name:
                    szy = i
                    found_month = True
                    break
            else:
                # 判断前一个月是否为闰月
                if i == 0 or lunar_month_names[i-1] != '闰' + lunar_month_name:
                    szy = i
                    found_month = True
                    break
        # 判断是否为闰月
        if is_leap_month and lunar_month_names[i] == '闰' + lunar_month_name:
            szy = i
            found_month = True
            break
    
    # 判断是否找到农历月份
    if not found_month:
        raise ValueError(f"无法找到农历月份: {lunar_date_str}")

    # 判断农历日期名称是否有效
    try:
        lunar_day_index = NLRQ.index(lunar_day_name)
    except ValueError:
        # 尝试按干支日名查找
        try:
            ganzhi_day_index = GANZHI_CYCLE.index(lunar_day_name)
            # 获取农历数据中第一个月的干支日名
            first_day_ganzhi_index = math.floor(new_moon_jds[szy] + 8 / 24 + 0.5 + 49) % 60
            # 计算农历日期名称的索引
            lunar_day_index = (ganzhi_day_index - first_day_ganzhi_index + 60) % 60
            
            # 判断该月是否有该日期
            if get_date_difference(new_moon_jds[szy] + lunar_day_index, new_moon_jds[szy + 1]) >= 0:
                raise ValueError(f"该月无 {lunar_day_name}")
        except ValueError as e:
            raise ValueError(f"无效的农历日期名称或干支日名: {lunar_day_name}. 错误: {e}")

    # 计算公历日期
    solar_jd = new_moon_jds[szy] + lunar_day_index
    solar_date_triple = jd_to_date(solar_jd, 8).triple()
    solar_date_str = f"{int(solar_date_triple[0])}-{int(solar_date_triple[1]):02d}-{int(solar_date_triple[2]):02d}"

    # 返回公历日期
    return (
        int(solar_date_triple[0]),
        int(solar_date_triple[1]),
        int(solar_date_triple[2])
    )
