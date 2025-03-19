
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# �ռ�������ģ��
hiddenimports = collect_submodules('tkinter') + \
                collect_submodules('networkx') + \
                collect_submodules('pandas') + \
                collect_submodules('datetime') + \
                collect_submodules('os') + \
                collect_submodules('time') + \
                collect_submodules('queue') + \
                collect_submodules('threading')

# �ռ������ļ�
datas = collect_data_files('data_loader') + \
        collect_data_files('path_finder') + \
        collect_data_files('calculate_money')