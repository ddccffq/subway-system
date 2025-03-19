
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# 收集所有子模块
hiddenimports = collect_submodules('tkinter') + \
                collect_submodules('networkx') + \
                collect_submodules('pandas') + \
                collect_submodules('datetime') + \
                collect_submodules('os') + \
                collect_submodules('time') + \
                collect_submodules('queue') + \
                collect_submodules('threading')

# 收集数据文件
datas = collect_data_files('data_loader') + \
        collect_data_files('path_finder') + \
        collect_data_files('calculate_money')