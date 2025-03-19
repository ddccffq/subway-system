# -*- coding: utf-8 -*-
import math
import tkinter as tk
from tkcalendar import DateEntry
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from data_loader import load_data
from path_finder import build_graph, find_shortest_path, find_quickest_paths_with_max_transfers, calculate_transfer_times, find_path_with_min_transfers, find_shortest_path_with_min_transfers
from calculate_money import calculate_money

# 加载数据
lines, stations, distances_df = load_data()
G = build_graph(distances_df)


# def find_none_nodes(G, lines):
#     none_nodes = []
#     for node in G.nodes:
#         # 遍历所有线路，检查节点是否存在且不为 None
#         node_found = False
#         for line in lines.values():
#             if line.get_station(node) is not None:
#                 node_found = True
#                 break
#         if not node_found:
#             none_nodes.append(node)
#     return none_nodes

# 示例调用
# none_nodes = find_none_nodes(G, lines)
# print(f"图中为 None 的节点: {none_nodes}")
# 更新时间
#时间复杂度O(1)
def update_time():
    # 获取当前时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')#'%Y-%m-%d %H:%M:%S'是时间格式，就是年月日时分秒
    # 更新时间
    time_label.config(text=f"{current_time}")
    # 每秒更新一次时间
    root.after(1000, update_time)  # 1000ms=1s
# 格式化路径文本
#时间复杂度O(1)
def format_path_text(start_station, end_station):
    # 从起点到终点的最短路径
    path_text = f"{start_station} -> {end_station}\n"
    return path_text
# 调整时间

#用来判断工作日还是周末
def is_weekend(planned_departure_day):
    return planned_departure_day >= 5


def adjust_time(first_train_time, last_train_time):
    # 确保 first_train_time 和 last_train_time 都是 datetime.time 类型
    if isinstance(first_train_time, datetime):
        first_train_time = first_train_time.time()
    if isinstance(last_train_time, datetime):
        last_train_time = last_train_time.time()
    
    # 如果末班车时间早于首班车时间
    if last_train_time < first_train_time:
        # 末班车时间加一天
        last_train_time = (datetime.combine(datetime.today(), last_train_time) + timedelta(days=1)).time()
    return first_train_time, last_train_time

def is_within_service_time(first_train_time, last_train_time, current_time):
    # 调整时间
    first_train_time, last_train_time = adjust_time(first_train_time, last_train_time)
    current_time = current_time.time()  # 确保 current_time 是 datetime.time 类型
    # 如果首末班车时间不为空，且当前时间在首末班车时间之间
    if first_train_time <= current_time <= last_train_time:
        return True
    if last_train_time < first_train_time:  # 跨越到第二天
        if current_time >= first_train_time or current_time <= last_train_time:
            return True
    return False

def is_right_time_(station, current_time, flag, planned_departure_day):
    if station is None:
        return "错误: 站点信息为空"
    # 判断是周末还是工作日
    if is_weekend(planned_departure_day):
        down_last_train_time = station.down_last_train_time_end
        up_last_train_time = station.up_last_train_time_end
    else:
        down_last_train_time = station.down_last_train_time
        up_last_train_time = station.up_last_train_time

    if flag == 'Down':
        # 如果首末班车时间为空
        if station.down_first_train_time is None and down_last_train_time is None:
            return f"错误: {station.station_name}站无车次"
        # 如果不在服务时间内
        if not is_within_service_time(station.down_first_train_time, down_last_train_time, current_time):
            return f"错误: {station.station_name}站非服务时间"
    elif flag == 'Up':
        # 如果首末班车时间为空
        if station.up_first_train_time is None and up_last_train_time is None:
            return f"错误: {station.station_name}站无车次"
        # 如果不在服务时间内
        if not is_within_service_time(station.up_first_train_time, up_last_train_time, current_time):
            return f"错误: {station.station_name}站非服务时间"
    return None

# 判断是否能到达       
#时间复杂度O(n)
def can_arrive(path):
    #得到起点站和终点站，和起点站的线路和终点站的线路
    line_name_start = G.edges[path[0], path[1]]['line']
    start_station = lines[line_name_start].get_station(path[0])
    line_name_end = G.edges[path[-2], path[-1]]['line']
    end_station = lines[line_name_end].get_station(path[-1])
    
    if start_station is None:
        messagebox.showerror("错误", f"起始站 {path[0]} 未找到")
        return False
    if end_station is None:
        messagebox.showerror("错误", f"终点站 {path[-1]} 未找到")
        return False

    #如果起点站和终点站都没有首末班车时间，则无法到达
    if start_station.down_first_train_time is None and start_station.up_first_train_time is None:
        messagebox.showerror("错误", f"起始站 {start_station.station_name} 未开通服务")
        return False
    if end_station.down_first_train_time is None and end_station.up_first_train_time is None:
        messagebox.showerror("错误", f"终点站 {end_station.station_name} 未开通服务")
        return False

    return True

# 通过站点名称获取站点，（不知道为什么输入"东四"会返回"东四十条"，所以人为加了一个判断）
def get_station_by_name(station_name):
    for line in lines.values():
        for station in line.stations:
            if station.station_name == station_name:
                return station
    return None

# 显示结果
#时间复杂度O(mn) 
# 显示结果
def display_result(paths):
    # 如果没有找到路径
    if not paths:
        messagebox.showerror("错误", "没有找到路径")
        return

    # 判断是否输入了出发时间
    if departure_time_entry.get() and departure_date_entry.get():
        planned_departure_time_str = departure_time_entry.get()
        planned_departure_date_str = departure_date_entry.get()
        try:
            # 修改日期解析格式
            planned_departure_time = datetime.strptime(f"{planned_departure_date_str} {planned_departure_time_str}", '%Y/%m/%d %H:%M')
            planned_departure_day = planned_departure_time.weekday()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的出发时间，格式为 HH:MM")
            return
    else:
        planned_departure_time = datetime.now()
        planned_departure_day = planned_departure_time.weekday()

    # 如果输入了不乘坐的线路
    if line_not_entry.get():
        # 过滤路径
        filtered_paths = []
        # 遍历路径
        for path in paths:
            keep_path = True
            for i in range(0, len(path)-1):
                line_name_start = G.edges[path[i], path[i+1]]['line']
                # 如果路径中包含不乘坐的线路，则跳过
                if line_name_start == line_not_entry.get():
                    keep_path = False
                    break
            if keep_path:
                filtered_paths.append(path)
        paths = filtered_paths
        if not paths:
            messagebox.showerror("错误", "没有找到路径")
            return

    # 如果输入了想要乘坐的线路
    if line_want_entry.get():
        filtered_paths = []
        for path in paths:
            keep_path = False
            for i in range(0, len(path)-1):
                line_name_start = G.edges[path[i], path[i+1]]['line']
                # 如果路径中包含想要乘坐的线路，则保留
                if line_name_start == line_want_entry.get():
                    keep_path = True
                    break
            if keep_path:
                filtered_paths.append(path)
        paths = filtered_paths
        if not paths:
            messagebox.showerror("错误", "没有找到路径")
    # 遍历路径，计算时间和距离
    for path in paths:
        # 创建结果窗口
        result_window = tk.Toplevel(root)
        result_window.title("查询结果")
        # 固定窗口大小
        result_text = tk.Text(result_window, width=70, height=int(70 * 0.618))
        result_text.pack(padx=20, pady=20)
        # 配置文本颜色
        result_text.tag_configure("color_tag", foreground='black')
        result_text.tag_configure("error_tag", foreground='red')

        # 如果不能到达，则跳过
        if not can_arrive(path):
            continue
        # 初始化时间和距离
        path_time = 0
        path_time_ = 0
        path_distance = 0
        current_time = planned_departure_time
        # 计算换乘次数
        transfer_times = calculate_transfer_times(G, path)
        # 遍历路径
        for i in range(0, len(path)-1):
            # 获取起点站和下一站
            line_name_start = G.edges[path[i], path[i+1]]['line']
            start_station = lines[line_name_start].get_station(path[i])
            next_station = lines[line_name_start].get_station(path[i+1])
            flag = G.edges[path[i], path[i+1]]['flag']
            # 如果是首尾站
            if i == 0 or i == len(path) - 1:
                # 如果不是首末班车时间，则无法出发
                error_message = is_right_time_(start_station, current_time, flag, planned_departure_day)
                if error_message:
                    # 标记错误
                    transfer_times = 0
                    result_text.insert(tk.END, format_path_text(start_station, next_station), "error_tag")
                    result_text.insert(tk.END, error_message + "\n", "error_tag")
                    break
                # 特别标注首尾站
                if i == 0:
                    # 第一行的“乘坐”和“->”特别标注
                    result_text.insert(tk.END, f"乘坐{line_name_start}\n", "color_tag")
                # 输出路径
                result_text.insert(tk.END, format_path_text(start_station, next_station), "color_tag")
                # 计算距离和时间
                path_distance += G.edges[path[i], path[i+1]]['distance']
                path_time = G.edges[path[i], path[i+1]]['time'] + 60
                # 更新时间
                current_time += timedelta(seconds=path_time)
            # 如果是换乘站
            elif 0 < i < len(path) - 1 and G.edges[path[i], path[i+1]]['line'] != G.edges[path[i-1], path[i]]['line']:
                error_message = is_right_time_(start_station, current_time, flag, planned_departure_day)
                # 特别标注换乘站
                result_text.insert(tk.END, f"乘坐{line_name_start}\n", "color_tag")
                if error_message:
                    transfer_times = 0
                    result_text.insert(tk.END, format_path_text(start_station, next_station), "error_tag")
                    result_text.insert(tk.END, error_message + "\n", "error_tag")
                    break
                # 更新数据
                result_text.insert(tk.END, format_path_text(start_station, next_station), "color_tag")
                path_distance += G.edges[path[i], path[i+1]]['distance']
                path_time = G.edges[path[i], path[i+1]]['time'] + 60 * 5
                current_time += timedelta(seconds=path_time)
            else:
                # 更新数据
                result_text.insert(tk.END, format_path_text(start_station, next_station), "color_tag")
                path_distance += G.edges[path[i], path[i+1]]['distance']
                path_time = G.edges[path[i], path[i+1]]['time'] + 60
                current_time += timedelta(seconds=path_time)
            path_time_ += path_time

        # 计算花费
        path_money = calculate_money(path_distance)
        # 输出结果
        result_text.insert(tk.END, f"\n总距离: {path_distance}米", "color_tag")
        #向上取整
        result_text.insert(tk.END, f"\n预计用时: {math.ceil(path_time_ / 60)}分钟", "color_tag")
        result_text.insert(tk.END, f"\n换乘次数: {transfer_times}", "color_tag")
        result_text.insert(tk.END, f"\n预计花费: {path_money}元", "color_tag")
        result_text.insert(tk.END, f"\n预计到达时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n", "color_tag")
# 获取所有站点名称，用于下拉列表
line_names = [line.line_name for line in lines.values()]

root = tk.Tk()
root.title("地铁路径查询")
# 固定窗口大小
root.geometry("1200x1200")  # 设置窗口大小
root.resizable(False, False)  # 禁用窗口缩放
root.configure(bg='#bdc3c7')  # 设置窗口背景颜色
# 创建一个ttk.Style实例
style = ttk.Style()

# 配置标签样式
style.configure('Custom.TLabel', background='#bdc3c7', foreground='#34495e', font=('宋体', 11))
# 配置按钮样式

style.configure('TButton', background='#bdc3c7',foreground='#7f8c8d', font=('宋体', 12, ))
# 创建输入框和标签,colum是列，row是行，padx是x方向的外边距，pady是y方向的外边距
#.grid是布局管理器，将组件放置在表格中，类似于excel的单元格

# 创建输入框和标签
ttk.Label(root, text="起点站:", style='Custom.TLabel').grid(column=0, row=0, padx=20, pady=20)
start_station_entry = tk.Entry(root, width=30, bg='#bdc3c7', fg='#2c3e50', font=('宋体', 11))  
start_station_entry.grid(column=1, row=0, padx=20, pady=20)

ttk.Label(root, text="终点站:", style='Custom.TLabel').grid(column=0, row=1, padx=20, pady=20)
end_station_entry = tk.Entry(root, width=30, bg='#bdc3c7', fg='#2c3e50', font=('宋体', 11))  
end_station_entry.grid(column=1, row=1, padx=20, pady=20)

ttk.Label(root, text="最大换乘次数:", style='Custom.TLabel').grid(column=0, row=6, padx=20, pady=20)
max_transfers_entry = tk.Entry(root, width=30, bg='#bdc3c7', fg='#2c3e50', font=('宋体', 11))
max_transfers_entry.grid(column=1, row=6, padx=20, pady=20)

ttk.Label(root, text="计划出发日期:", style='Custom.TLabel').grid(column=0, row=8, padx=20, pady=20)
departure_date_entry = DateEntry(root, width=27, bg='#bdc3c7', fg='#2c3e50', font=('宋体', 11), date_pattern='yyyy/MM/dd')
departure_date_entry.grid(column=1, row=8, padx=20, pady=20)

ttk.Label(root, text="计划出发时间(HH:MM):", style='Custom.TLabel').grid(column=0, row=9, padx=20, pady=20)
departure_time_entry = tk.Entry(root, width=30, bg='#bdc3c7', fg='#2c3e50', font=('宋体', 11))
departure_time_entry.grid(column=1, row=9, padx=20, pady=20)

ttk.Label(root, text="希望不乘坐的线路:", style='Custom.TLabel').grid(column=0, row=10, padx=20, pady=20)
ttk.Label(root, text="想要乘坐的线路:", style='Custom.TLabel').grid(column=0, row=11, padx=20, pady=20)

# 创建下拉列表并绑定选择事件
def on_combobox_select_not(event):
    selected_line = line_not_combobox.get()
    line_not_entry.delete(0, tk.END)
    line_not_entry.insert(0, selected_line)

def on_combobox_select_want(event):
    selected_line = line_want_combobox.get()
    line_want_entry.delete(0, tk.END)
    line_want_entry.insert(0, selected_line)
#Combobox是下拉列表控件
line_not_entry = tk.Entry(root, width=30,bg='#bdc3c7', fg='#2c3e50', font=('宋体', 11))
line_not_entry.grid(column=1, row=10, padx=20, pady=20)

line_not_combobox = ttk.Combobox(root, values=line_names, width=27)
line_not_combobox.grid(column=2, row=10, padx=20, pady=20)
line_not_combobox.bind("<<ComboboxSelected>>", on_combobox_select_not)

line_want_entry = tk.Entry(root, width=30,bg='#bdc3c7', fg='#2c3e50', font=('宋体', 11))
line_want_entry.grid(column=1, row=11, padx=20, pady=20)

line_want_combobox = ttk.Combobox(root, values=line_names, width=27)
line_want_combobox.grid(column=2, row=11, padx=20, pady=20)
line_want_combobox.bind("<<ComboboxSelected>>", on_combobox_select_want)

# 创建按钮,command是点击按钮后执行的函数
shortest_path_button = ttk.Button(root, text="最短路径", style='TButton',  command=lambda: display_result(find_shortest_path(G, start_station=start_station_entry.get(), end_station=end_station_entry.get())))
shortest_path_button.grid(column=0, row=2, columnspan=2, padx=20, pady=20)

quickest_path_button = ttk.Button(root, text="期望最大换乘次数下最少时间", style='TButton',  command=lambda: display_result(find_quickest_paths_with_max_transfers(G, start_station=start_station_entry.get(), end_station=end_station_entry.get(), max_transfers=max_transfers_entry.get())))
quickest_path_button.grid(column=0, row=7, columnspan=2,padx=20, pady=20)

min_transfers_button = ttk.Button(root, text="输出所有最少换乘次数", style='TButton', command=lambda: display_result(find_path_with_min_transfers(G, start_station=start_station_entry.get(), end_station=end_station_entry.get(), max_transfers=0)))
min_transfers_button.grid(column=0, row=3, columnspan=2, padx=20, pady=20)

min_shortest_button = ttk.Button(root, text="输出最短最少换乘次数", style='TButton', command=lambda: display_result(find_shortest_path_with_min_transfers(G, start_station=start_station_entry.get(), end_station=end_station_entry.get(), max_transfers=0)))
min_shortest_button.grid(column=0, row=4, columnspan=2, padx=20, pady=20)

# 定义刷新函数
def refresh():
    # 清空所有可以输入的文本框里的内容
    start_station_entry.delete(0, tk.END)
    end_station_entry.delete(0, tk.END)
    max_transfers_entry.delete(0, tk.END)
    departure_time_entry.delete(0, tk.END)
    line_not_entry.delete(0, tk.END)
    line_want_entry.delete(0, tk.END)
    line_not_combobox.set('')
    line_want_combobox.set('')
        # 关闭所有打开的窗口
    for window in root.winfo_children():
        if isinstance(window, tk.Toplevel):
            window.destroy()

# 创建刷新按钮
refresh_button = ttk.Button(root, text="刷新", style='TButton', command=refresh)
refresh_button.grid(column=8, row=8, columnspan=2, padx=20, pady=20)
# 启动时间更新
time_label = ttk.Label(root, text="", style='Custom.TLabel')
time_label.grid(column=0, row=12, padx=20, pady=20)
update_time()

# 运行主循环
root.mainloop()