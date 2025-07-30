from .print_opt import printPro, clear_printpro_logs
import requests
import pkg_resources
import sys
import threading
import os

__all__ = ['printPro', 'clear_printpro_logs']

# 读取版本号
try:
    # 获取当前文件所在目录的上一级目录
    package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    version_path = os.path.join(package_root, 'version.txt')
    print(version_path)
    # 如果是已安装的包，尝试从包内读取
    if not os.path.exists(version_path):
        try:
            __version__ = pkg_resources.get_distribution('print_opt').version
        except Exception:
            __version__ = '0.1.1'  # 默认版本号，如果无法获取
    else:
        with open(version_path, 'r', encoding='utf-8') as f:
            __version__ = f.read().strip()
except Exception:
    __version__ = '0.1.1'  # 默认版本号，如果无法获取

def check_latest_version():
    """
    检查PyPI上print_opt的最新版本，如果有新版本则显示警告
    """
    try:
        # 在后台线程中运行，避免阻塞导入过程
        threading.Thread(target=_check_version_worker, daemon=True).start()
    except Exception:
        # 如果检查失败，静默处理
        pass

def _check_version_worker():
    """后台运行的版本检查工作函数"""
    try:
        # 获取当前安装的版本
        current_version = __version__
        
        # 从PyPI获取最新版本
        response = requests.get('https://pypi.org/pypi/print_opt/json', timeout=2)
        latest_version = response.json()['info']['version']
        
        # 比较版本号
        if current_version != latest_version:
            # 使用ANSI转义码生成黄色警告文本
            warning = '\033[93mPlease install the latest version of print_opt ==>  pip install --upgrade print_opt\033[0m'
            print(warning, file=sys.stderr)
    except Exception:
        # 如果检查失败，静默处理
        pass

# 导入时自动检查版本
check_latest_version()
