# printPro

一个简单易用的 Python 日志工具，用于调试输出。

## 功能特点

- 支持多种数据类型的输出（字符串、字典、列表等）
- 可配置的输出格式（时间戳、换行数等）
- 支持临时日志和持久日志
- 多进程安全
- 自动清理过期的临时日志
- 在生产环境中自动禁用（不影响性能）

## 推荐配置  
- 在.gitignore中忽略printProLog文件夹
- 对于热更新的服务，启动时请忽略printProLog文件夹

## 安装

```bash
pip install print_opt
```

## 快速开始

```python
from print_opt import printPro

# 基本用法
printPro("Hello, World!")

# 输出字典
data = {"name": "张三", "age": 30}
printPro(data)

# 带时间戳的输出
printPro("带时间戳的消息", show_timestamp=True)

# 持久化日志（不会在程序重启时清除）
printPro("这是一条持久化日志", clear_on_restart=False)

# 输出到指定文件
printPro("输出到特定文件", filename="my_log.txt")

# 输出到指定文件夹
printPro("输出到指定文件夹", folder="subdir/logs")
```

## API 文档

### printPro 函数

```python
printPro(
    content,              # 要输出的内容，可以是任意类型
    filename="default.txt", # 输出文件名
    clear_on_restart=True,  # 是否在程序重启时清空文件
    show_timestamp=False,   # 是否显示时间戳
    line_breaks=1,          # 记录间的空行数
    folder=None,            # 子文件夹路径
    forceWrite=True         # 是否强制覆盖模式
)
```

### 其他实用函数

```python
# 清空所有日志（不包括持久化日志）
from print_opt import clear_printpro_logs
clear_printpro_logs()

# 清空所有日志（包括持久化日志）
clear_printpro_logs(include_persistent=True)
```

## 许可证

MIT

## 作者

GDluCk 