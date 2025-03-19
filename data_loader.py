# -*- coding: utf-8 -*-
import pandas as pd
import os
from subway import Subway_Station, Subway_Line

# 从Excel文件中加载数据
def load_data():
    #时间复杂度O(n)
    excel_file = os.path.join('data', 'Data.xlsx')
    lines_df = pd.read_excel(excel_file, sheet_name='Lines')
    stations_df = pd.read_excel(excel_file, sheet_name='Stations')
    distances_df = pd.read_excel(excel_file, sheet_name='Distances')
    # 创建地铁线路字典
    #时间复杂度O(n)
    lines = {}
    # 遍历地铁线路数据
    for index, row in lines_df.iterrows():
        line = Subway_Line(row['Line_Name'], row['Line_Speed'])
        # 将地铁线路加入到字典中
        lines[row['Line_Name']] = line
    # 创建地铁站点字典
    #时间复杂度O(n)
    stations = {}
    # 遍历地铁站点数据
    for index, row in stations_df.iterrows():
        station = Subway_Station(
            Station_Name=row['Station_Name'],
            Station_Lines=row['Station_Line'],
            Down_First_Train_Time=row['Down_First_Train_Time'],
            Down_Last_Train_Time=row['Down_Last_Train_Time'],
            Down_Last_Train_Time_End=row['Down_Last_Train_Time_End'],
            Up_First_Train_Time=row['Up_First_Train_Time'],
            Up_Last_Train_Time=row['Up_Last_Train_Time'],
            Up_Last_Train_Time_End=row['Up_Last_Train_Time_End']
        )
        stations[row['Station_Name']] = station
        # 将站点加入到对应的线路中
        lines[row['Station_Line']].add_station(station)
    return lines, stations, distances_df