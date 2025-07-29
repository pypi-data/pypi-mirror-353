#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速开始 - 最简单的使用示例
安装: pip install dtraderhq-python-client
"""

import asyncio
from dtraderhq_client import DTraderHQClient


async def main():
    # 创建客户端
    client = DTraderHQClient(
        url="ws://localhost:8080/ws",
        token="your_jwt_token_here"
    )
    
    # 设置数据回调
    client.on_data = lambda data: print(f"📈 {data.symbol}: ¥{data.price}")
    client.on_error = lambda error: print(f"❌ 错误: {error}")
    
    try:
        # 连接并认证
        await client.connect()
        await client.authenticate()
        
        # 订阅股票
        await client.subscribe("000001.SZ")
        
        print("🚀 开始接收数据...")
        await asyncio.sleep(10)  # 运行10秒
        
    finally:
        await client.close()
        print("👋 连接已关闭")


if __name__ == "__main__":
    asyncio.run(main())