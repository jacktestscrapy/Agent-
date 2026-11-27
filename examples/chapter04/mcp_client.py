"""通过 MCP 标准输入输出客户端发现并调用本地服务端。"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    # 使用当前 Python 解释器启动同目录服务端，避免拼接命令行字符串。
    server_path = Path(__file__).with_name("mcp_server.py")
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
    )

    # 客户端管理服务端子进程和协议数据流，并负责维护 MCP 会话。
    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 初始化协议会话后查询服务端提供的工具。
            await session.initialize()
            tools = await session.list_tools()
            print(f"已发现 {len(tools.tools)} 个工具。")
            # 调用发现的只读工具；服务端错误应显式报告。
            result = await session.call_tool(
                "search_knowledge",
                {"查询内容": "请介绍模型上下文协议如何连接智能体和工具。"},
            )
            if result.isError:
                raise RuntimeError(f"模型上下文协议工具调用失败：{result.content}")
            # 协议返回内容可能包含多种类型，这里只输出其中的文本内容。
            for item in result.content:
                if hasattr(item, "text"):
                    print(item.text)


if __name__ == "__main__":
    # 运行异步客户端入口，并等待 MCP 发现和调用完成。
    asyncio.run(main())
