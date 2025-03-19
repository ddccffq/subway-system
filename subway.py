# -*- coding: utf-8 -*-
from datetime import datetime
import pandas as pd

# 从字符串中解析时间
# 时间复杂度O(1)
def parse_time(time_value):
    # 如果时间值为空，则返回None
    if pd.isna(time_value):
        return None
    # 如果时间值是字符串，则尝试解析时间
    if isinstance(time_value, str):
        try:
            return datetime.strptime(time_value, '%H:%M:%S')# 将字符串转换为时间
        except ValueError:
            return None
    # 如果时间值是浮点数，则返回None
    if isinstance(time_value, float):
        return None
    return time_value

# 地铁站点类
#时间复杂度O(1)
class Subway_Station:
    # 初始化地铁站点
    def __init__(self, Station_Name, Station_Lines, Down_First_Train_Time=None, Down_Last_Train_Time=None, Down_Last_Train_Time_End=None,Up_First_Train_Time=None, Up_Last_Train_Time=None,Up_Last_Train_Time_End=None):
        self.station_name = Station_Name
        self.station_lines = Station_Lines if isinstance(Station_Lines, list) else [Station_Lines]
        self.down_first_train_time = parse_time(Down_First_Train_Time)
        self.down_last_train_time = parse_time(Down_Last_Train_Time)
        self.down_last_train_time_end=  parse_time(Down_Last_Train_Time_End)
        self.up_first_train_time = parse_time(Up_First_Train_Time)
        self.up_last_train_time = parse_time(Up_Last_Train_Time)
        self.up_last_train_time_end=    parse_time(Up_Last_Train_Time_End)
    # 获取站点名称
    def get_name(self):
        return self.station_name
    # 获取站点所属线路
    def get_lines(self):
        return self.station_lines
    # 获取下行首班车时间
    def get_down_first_train_time(self):
        return self.down_first_train_time
    # 获取下行末班车时间
    def get_down_last_train_time(self):
        return self.down_last_train_time
    #获取下行末班车周末
    def get_down_last_train_time_end(self):
        return self.down_last_train_time_end
    # 获取上行首班车时间
    def get_up_first_train_time(self):
        return self.up_first_train_time
    # 获取上行末班车时间
    def get_up_last_train_time(self):
        return self.up_last_train_time
    #获取上行末班车周末
    def get_up_last_train_time_end(self):
        return self.up_last_train_time_end
    # 将站点信息转换为字典
    def to_dict(self):
        return {
            'station_name': self.station_name,
            'station_lines': self.station_lines,
            # 字符串格式化时间
            'down_first_train_time': self.down_first_train_time.strftime('%H:%M:%S') if self.down_first_train_time else None,
            'down_last_train_time': self.down_last_train_time.strftime('%H:%M:%S') if self.down_last_train_time else None,
            'down_last_train_time_end':self.down_last_train_time_end('%H:%M:%S') if self.down_last_train_time_end else None,
            'up_first_train_time': self.up_first_train_time.strftime('%H:%M:%S') if self.up_first_train_time else None,
            'up_last_train_time': self.up_last_train_time.strftime('%H:%M:%S') if self.up_last_train_time else None,
            'up_last_train_time_end':self.up_last_train_time_end('%H:%M:%S') if self.up_last_train_time_end else None
        }
    # 将站点信息转换为字符串
    def __repr__(self):
        return f"Subway_Station({self.station_name})"
# 地铁线路类
#时间复杂度O(1)
class Subway_Line:
    # 初始化地铁线路
    def __init__(self, Line_Name, Line_Speed):
        self.line_name = Line_Name
        self.line_speed = Line_Speed
        self.stations = []
    # 获取线路名称
    def get_speed(self):
        return self.line_speed
    # 获取线路速度
    def add_station(self, station):
        self.stations.append(station)
    # 获取线路站点
    def get_station(self, station_name):
        for station in self.stations:
            if station.station_name == station_name:
                return station
        return None
    # 将线路信息转换为字典
    def to_dict(self):
        return {
            'line_name': self.line_name,
            'line_speed': self.line_speed
        }
    
    