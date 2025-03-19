# -*- coding: utf-8 -*-
import networkx as nx
from collections import deque
from tkinter import messagebox
from data_loader import load_data

## 从Excel文件中加载数据
lines, stations, distances_df = load_data()

#判断输入的起点和终点站名是否有效
def is_right_station(start_station, end_station):
    #如果起点站名和终点站名不在站点字典中，返回错误
    #时间复杂度O(1)
    if start_station not in stations:
        messagebox.showerror("错误", "请输入有效的起点站名")
        return False
    if end_station not in stations:
        messagebox.showerror("错误", "请输入有效的终点站名")
        return False
    if start_station == end_station:
        messagebox.showerror("错误", "起点和终点站名不能相同")
        return False
    return True

#构建地铁图
#时间复杂度O(2n-2)
def build_graph(distances_df):
    G = nx.DiGraph()
    for _, row in distances_df.iterrows():
        G.add_edge(row['Station1'], row['Station2'], distance=row['Distance'], flag=row['Di_Flag'], line=row['Line_Flag'], time=row['Time'])
    return G
#计算换乘次数
#时间复杂度O(n)
def calculate_transfer_times(G, paths):
    # 如果路径为空，返回None
    if paths == None:
        messagebox.showerror("错误", "没有找到路径")
        return None
    #初始化换乘次数
    transfer_times = 0
    last_line = None
    #遍历路径
    for i in range(1, len(paths)):
        current_line = G[paths[i - 1]][paths[i]]['line']
        if current_line != last_line:
            transfer_times += 1
            last_line = current_line
    return transfer_times - 1  # 算的是地铁线数量，换成次数减一
#广度优先搜索，找到在最大换乘次数内的所有路径
#时间复杂度O(n)
def BFS(G, start_station, end_station, max_transfers):
    try:
        #时间复杂度O(1)
        queue = deque([(start_station, [start_station])])  # 初始化队列, 将起始站加入队列, 并将起始站作为路径的第一个元素
        valid_paths = []  # 用于存储有效路径
        while queue:
            #时间复杂度O(1)
            current_station, path = queue.popleft()  # 取出队列的第一个元素
            # 如果当前站点是终点站，将路径加入到有效路径中
            if current_station == end_station:
                valid_paths.append(path)
                continue
            # 遍历当前站点的邻居站点
            #时间复杂度O(node+edge)
            for neighbor in G.neighbors(current_station):
                if neighbor not in path:
                    # 如果当前路径的换乘次数小于等于最大换乘次数，将邻居站点加入队列
                    new_path = path + [neighbor]
                    if calculate_transfer_times(G, new_path) <= int(max_transfers):
                        queue.append((neighbor, new_path))
        return valid_paths
    # 没有路径，返回None
    except Exception as e:
        messagebox.showerror("错误", f"没有路径: {e}")
        return []
#计算最短路径
#时间复杂度O(n)
def Dijkstra(G, start_station, end_station):
    # 初始化距离字典
    distances = {node: float('inf') for node in G.nodes}
    distances[start_station] = 0
    # 初始化前驱节点字典
    previous_nodes = {node: None for node in G.nodes}
    # (当前距离, 当前节点, 当前路径)
    queue = deque([(0, start_station, [start_station])])  

    while queue:
        # 取出队列的第一个元素
        current_distance, current_node, path = queue.popleft()
        # 如果当前节点是终点站，返回路径
        if current_node == end_station:
            return path
        # 遍历当前节点的邻居节点
        #时间复杂度O(node+edge)
        for neighbor in G.neighbors(current_node):
            weight = G[current_node][neighbor]['distance']
            distance = current_distance + weight
            # 如果新的距离小于原来的距离，更新距离和前驱节点
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                new_path = path + [neighbor]
                queue.append((distance, neighbor, new_path))

    return None
#找到最短路径
#时间复杂度O(n)
def find_shortest_path(G, start_station, end_station):
    # 如果起点和终点站名无效，返回空列表
    if not is_right_station(start_station, end_station):
        return []
    # 使用Dijkstra算法找到最短路径
    try:
        valid_path = Dijkstra(G, start_station, end_station)
        if valid_path:
            return [valid_path]
        else:
            messagebox.showerror("错误", "没有找到路径")
            return []
    except Exception as e:
        messagebox.showerror("错误", f"发生错误: {e}")
        return []
#找到最短时间路径
#时间复杂度O(n)
def find_quickest_paths_with_max_transfers(G, start_station, end_station, max_transfers):
    # 如果起点和终点站名无效，返回空列表
    if not is_right_station(start_station, end_station):
        return []
    #找到所有路径
    all_paths = BFS(G, start_station, end_station, max_transfers)
    #如果没有找到路径，返回空列表
    if not all_paths:
        return []  # 没有找到路径
    try:
        #初始化最短路径
        shortest_paths = []
        quickest_path=None
        min_time = float('inf')
        #遍历所有路径
        #时间复杂度O(n)
        for path in all_paths:
            transfer_times = calculate_transfer_times(G, path)
            #计算路径的时间
            time = nx.shortest_path_length(G, source=path[0], target=path[-1], weight='time') + (len(path) - 2) * 60 + transfer_times * 5 * 60
            #如果时间小于最小时间，更新最小时间和最短路径
            if time < min_time:
                quickest_path = path
                min_time = time
        #将最短路径加入到最短路径中
        if quickest_path:
            shortest_paths.append(quickest_path)
            return shortest_paths
    except Exception as e:
        messagebox.showerror("错误", f"没有找到路径: {e}")
        return []
#找到最短距离路径
#时间复杂度O(n)
def find_shortest_path_with_min_transfers(G, start_station, end_station, max_transfers):
    # 如果起点和终点站名无效，返回空列表
    if not is_right_station(start_station, end_station):
        return []
    #找到所有路径
    path_found = False
    #遍历最大换乘次数，默认为6
    for i in range(max_transfers, 7):
        #如果找到路径，跳出循环
        if path_found:
            break
        #使用广度优先搜索找到在最大换乘次数内的所有路径
        all_paths = BFS(G, start_station, end_station, i)
        #如果没有找到路径，继续循环
        if not all_paths:
            continue  # 没有路径，继续循环
        #初始化最短路径
        shortest_path_=[]
        shortest_path = None
        min_distance = float('inf')
        #遍历所有路径
        for path in all_paths:
            distance = 0
            #计算路径的距离
            for i in range(0,len(path)-1):
                distance += G[path[i]][path[i+1]]['distance']
            #如果距离小于最小距离，更新最小距离和最短路径
            if int(distance) < min_distance:
                min_distance = distance
                shortest_path = path
        #将最短路径加入到最短路径中
        if shortest_path:
            shortest_path_.append(shortest_path)
            path_found =True
            #返回最短路径
            return shortest_path_
    if not path_found:
        messagebox.showerror("错误", "没有找到路径")
        return []
    
#找到最少换乘路径    
#时间复杂度O(7n)
def find_path_with_min_transfers(G, start_station, end_station, max_transfers):
    # 如果起点和终点站名无效，返回空列表
    if not is_right_station(start_station, end_station):
        return []
    path_found = False
    #遍历最大换乘次数，默认为6
    for i in range(max_transfers, 7):
        if path_found:
            break
        all_paths = BFS(G, start_station, end_station, i)
        if not all_paths:
            continue  # 没有路径，继续循环
        else:
            path_found =True
            #返回路径
        return all_paths
    if not path_found:
        messagebox.showerror("错误", "没有找到路径")
        return []
    
