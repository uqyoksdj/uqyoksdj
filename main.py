#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
视频下载和处理工具主程序入口
"""

import sys
import os

# 将src目录添加到模块搜索路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.append(src_dir)

# 导入UI模块
from src.ui.UI import MainApp

if __name__ == "__main__":
    # 启动应用程序
    app = MainApp()
    app.run() 