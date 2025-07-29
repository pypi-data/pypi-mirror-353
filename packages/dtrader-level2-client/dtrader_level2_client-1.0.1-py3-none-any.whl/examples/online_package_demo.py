#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用线上包的最简单demo
安装命令: pip install dtraderhq-python-client
"""

import asyncio
from dtraderhq_client import DTraderHQClient, MarketData


async def on_data(data: MarketData):
    """处理市场数据"""
    print(f"收到数据: {data.symbol} - 价格: {data.price} - 时间: {data.timestamp}")


async def on_error(error: str):
    """处理错误"""
    print(f"错误: {error}")


async def on_connected():
    """连接成功回调"""
    print("WebSocket连接成功")


async def on_authenticated():
    """认证成功回调"""
    print("认证成功")


async def main():
    """主函数"""
    # 创建客户端
    client = DTraderHQClient(
        url="ws://localhost:8080/ws",
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6InNvb2JveSIsImV4cCI6MTc4MDE5MTMyNSwiaWF0IjoxNzQ5MDg3MzI1fQ.qwYExSfL2qz5G4u6rhXxPYr3wkezmwOCYb6OfL3tVZk"
    )
    
    # 设置事件回调
    client.on_data = on_data
    client.on_error = on_error
    client.on_connected = on_connected
    client.on_authenticated = on_authenticated
    
    try:
        # 连接到服务器
        await client.connect()
        
        # 认证
        await client.authenticate()
        
        # 订阅股票数据
        await client.subscribe("000001.SZ")
        
        print("开始接收数据，按Ctrl+C退出...")
        
        # 运行5秒后自动退出（用于演示）
        await asyncio.sleep(5)
        
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 关闭连接
        await client.close()
        print("连接已关闭")


if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())