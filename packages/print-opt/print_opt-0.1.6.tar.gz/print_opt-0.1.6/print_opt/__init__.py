from .print_opt import printPro, clear_printpro_logs
import requests
import pkg_resources
import sys
import threading
import os
import time

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
        
        # 从PyPI获取最新版本，增加超时时间
        max_retries = 2
        retry_count = 0
        timeout_seconds = 8  # 增加超时时间到8秒
        
        while retry_count <= max_retries:
            try:
                response = requests.get('https://pypi.org/pypi/print_opt/json', timeout=timeout_seconds)
                latest_version = response.json()['info']['version']
                
                # 比较版本号
                if current_version != latest_version:
                    # 使用ANSI转义码生成警告文本
                    redWarning = '\033[91mWARNING: Please install the latest version of print_opt ==>  pip install --upgrade print_opt\033[0m'
                    yellowWarning = '\033[93mWARNING: Please install the latest version of print_opt ==>  pip install --upgrade print_opt\033[0m'
                    print(redWarning, file=sys.stderr)
                break  # 成功获取版本信息，跳出循环
            except Exception:
                retry_count += 1
                if retry_count > max_retries:
                    # 所有重试都失败后，静默处理
                    pass
                else:
                    # 短暂延迟后重试
                    time.sleep(0.5)
    except Exception:
        # 如果检查失败，静默处理
        pass


# 导入时自动检查版本
check_latest_version()
