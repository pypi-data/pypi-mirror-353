#!/usr/bin/env python3
"""
DTraderHQ Python WebSocket客户端安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dtrader-level2-client",
    version="1.0.0",
    author="dtrader",
    author_email="admin@dtrader.store",
    description="DTrader Level2 WebSocket API Python客户端",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DTrader-store",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            # 如果需要命令行工具，可以在这里添加
        ],
    },
    keywords="websocket, stock, trading, finance, api, client",
    project_urls={
        "Bug Reports": "https://github.com/DTrader-store/level2-client-python/issues",
        "Source": "https://github.com/DTrader-store/level2-client-python",
        "Documentation": "https://github.com/DTrader-store/level2-client-python/blob/main/client/python/README.md",
    },
    include_package_data=True,
    zip_safe=False,
)