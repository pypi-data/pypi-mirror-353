#!/usr/bin/env python3
"""CodingConverse MCP Server Entry Point

允许通过 python -m coding_converse 运行MCP服务器
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())