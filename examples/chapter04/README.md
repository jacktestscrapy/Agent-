# 第4章演示代码

本章提供三类示例：

- `tool_registry.py`：不依赖模型接口的轻量工具注册表，演示工具登记、参数定义、允许列表分发和输入校验。
- `function_calling_agent.py`：使用 DeepSeek 兼容接口执行函数调用往返；模型提出调用请求，由程序校验并执行已登记工具。
- `mcp_server.py` / `mcp_client.py`：通过官方 MCP Python 开发工具包暴露和发现教学工具，使用标准输入输出完成协议调用。

## 环境准备

Python 3.10+，在仓库根目录执行：

```bash
pip install -r requirements.txt
```

函数调用示例需要在项目根目录 `.env` 中设置：

```dotenv
DEEPSEEK_API_KEY=你的_API_Key
DEEPSEEK_MODEL=deepseek-chat
```

## 运行示例

请在仓库根目录执行：

```bash
python examples/chapter04/tool_registry.py
python examples/chapter04/function_calling_agent.py
python examples/chapter04/mcp_client.py
```

`mcp_client.py` 会自动以子进程方式启动 `mcp_server.py`，无需手工启动服务端。也可以单独启动服务端检查其进程行为；标准输入输出服务端需要由兼容客户端管理输入输出。

所有工具只使用内置教学数据，不连接真实服务或执行写操作。函数调用示例需要可用的模型接口密钥；工具注册表和 MCP 示例可在本地运行。
