#!/usr/bin/env python3
"""CodingConverse MCP Server

一个MCP服务，为AI代码编辑器提供与用户对话的能力。
通过stdio协议与AI编辑器通信，当需要用户输入时显示对话框。
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from message_dialog import show_message_dialog


class MCPServer:
    """MCP服务器类"""
    
    def __init__(self):
        self.capabilities = {
            "tools": {
                "listChanged": False
            }
        }
        
        self.tools = [
            {
                "name": "ask_user",
                "description": "向用户询问问题并获取回复。当AI编辑器遇到需要用户决策或输入的情况时使用。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "要向用户显示的消息内容"
                        },
                        "title": {
                            "type": "string",
                            "description": "对话框标题",
                            "default": "AI编辑器询问"
                        }
                    },
                    "required": ["message"]
                }
            }
        ]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": self.capabilities,
                        "serverInfo": {
                            "name": "CodingConverse",
                            "version": "2.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.tools
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "ask_user":
                    result = await self.ask_user(
                        message=arguments.get("message", ""),
                        title=arguments.get("title", "AI编辑器询问")
                    )
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result
                                }
                            ]
                        }
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def ask_user(self, message: str, title: str = "AI编辑器询问", placeholder: str = "请输入您的回复...") -> str:
        """向用户询问问题"""
        try:
            # 在新的事件循环中运行对话框
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = show_message_dialog(
                    message=message,
                    title=title,
                    placeholder=placeholder
                )
                return result if result else "Continue"
            finally:
                loop.close()
        
        except Exception as e:
            return f"显示对话框时出错: {str(e)}"
    
    async def run(self):
        """运行MCP服务器"""
        while True:
            try:
                # 从stdin读取请求
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                # 解析JSON请求
                try:
                    request = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                
                # 处理请求
                response = await self.handle_request(request)
                
                # 发送响应
                print(json.dumps(response, ensure_ascii=False), flush=True)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                # 发送错误响应
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Server error: {str(e)}"
                    }
                }
                print(json.dumps(error_response, ensure_ascii=False), flush=True)


async def main():
    """主函数"""
    server = MCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())