"""
test_lunar_calendar.py

此模块包含对 lunar_calendar 包中日期转换功能的单元测试。
"""

import unittest
from lunar_calendar.converters import solar_to_lunar, lunar_to_solar

class TestLunarCalendar(unittest.TestCase):
    """
    测试公历与农历转换功能。
    """

    def test_solar_to_lunar(self):
        """
        测试公历转农历功能。
        """
        # 2025年1月29日 是 农历甲辰年 丁丑月 戊戌日 正月初一
        self.assertEqual(solar_to_lunar("2025-01-29"), ("甲辰", "丁丑", "戊戌", "正月", "初一"))

    def test_lunar_to_solar(self):
        """
        测试农历转公历功能。
        """
        # 农历甲辰年 正月初一 -> 2025-01-29
        self.assertEqual(lunar_to_solar(2025, "正月初一"), (2025, 1, 29))


if __name__ == '__main__':
    unittest.main()
