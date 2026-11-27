"""使用 MCP 开发工具包提供只读的教学工具。"""

from mcp.server.fastmcp import FastMCP

# 创建 MCP 服务端；登记的工具通过标准输入输出提供给配套客户端。
mcp = FastMCP("chapter04-teaching-tools")


@mcp.tool()
def search_knowledge(查询内容: str) -> str:
    """在本地教学知识库中搜索内容。"""
    # 使用本地教学数据演示检索，不读取外部文件或服务。
    entries = {
        "智能体": "智能体可以根据目标选择行动并调用工具推进任务。",
        "工作流": "工作流按照预先定义的步骤和控制逻辑执行任务。",
        "协议": "模型上下文协议用于连接智能体应用与外部能力。",
    }
    query_lower = 查询内容.lower()
    matches = [text for key, text in entries.items() if key.lower() in query_lower]
    return "\n".join(matches) if matches else "知识库中没有找到匹配内容。"


@mcp.tool()
def get_product_info(产品名称: str) -> str:
    """查询教学用产品说明。"""
    # 返回预置产品说明；未知产品不触发外部查询。
    products = {
        "智能体平台": "支持接入模型、调用工具和编排工作流。",
        "知识库系统": "支持导入文档、检索内容和回答问题。",
    }
    return products.get(产品名称, "没有找到对应的产品信息。")


if __name__ == "__main__":
    # 标准输入输出由 MCP 客户端管理，标准输出仅用于传输协议消息。
    mcp.run(transport="stdio")
