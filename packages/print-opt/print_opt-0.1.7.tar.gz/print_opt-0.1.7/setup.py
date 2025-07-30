from setuptools import setup, find_packages
import os

# 读取版本号
with open('version.txt', 'r', encoding='utf-8') as f:
    version = f.read().strip()

setup(
    name='print_opt',  # 包名
    version=version,  # 从version.txt读取版本号
    author='GDluCk',  # 作者名
    author_email='1477482440@qq.com',  # 作者邮箱
    description='用于调试输出的高级日志工具',  # 简短描述
    long_description=open('README.md', 'r', encoding='utf-8').read(),  # 详细描述
    long_description_content_type='text/markdown',  # 详细描述的类型
    url='https://github.com/afk101/printPro',  # 项目主页
    packages=find_packages(),  # 自动发现包
    install_requires=[
        'psutil',  # 依赖项
        'requests',  # 用于版本检查
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # 支持的 Python 版本
    include_package_data=True,  # 包含MANIFEST.in中指定的文件
) 