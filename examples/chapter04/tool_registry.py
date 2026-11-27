"""使用轻量工具注册表登记工具并校验调用参数。"""

from __future__ import annotations

# 标准库：json 用于解析模型传入的 JSON 参数。
import json
# 标准库：用于描述工具函数、映射参数和数据类。
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any


# 工具统一接收已经校验过的参数字典，并返回文本结果。
Handler = Callable[[dict[str, Any]], str]


class ToolInputError(ValueError):
    """工具名称或调用参数不符合注册表定义时抛出的异常。"""


# 参数类型与 Python 值检查函数的映射；避免布尔值被误判为整数。
_JSON_TYPES: dict[str, Callable[[Any], bool]] = {
    "string": lambda value: isinstance(value, str),
    "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
    "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
    "boolean": lambda value: isinstance(value, bool),
}

# 用中文说明参数类型，便于将校验错误直接展示给学习者。
_TYPE_NAMES = {
    "string": "文本",
    "integer": "整数",
    "number": "数字",
    "boolean": "布尔值",
}


@dataclass(frozen=True)
class Tool:
    # 保存工具名称、用途说明、参数定义和实际执行函数。
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Handler


class ToolRegistry:
    def __init__(self) -> None:
        # 仅允许调用已经明确登记的工具。
        self._tools: dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Handler,
    ) -> None:
        # 注册时先检查名称和参数定义，避免无效工具进入注册表。
        if not name or not name.replace("_", "").isalnum():
            raise ValueError("工具名称只能包含英文字母、数字和下划线。")
        if name in self._tools:
            raise ValueError(f"工具已经登记：{name}")
        if parameters.get("type") != "object":
            raise ValueError("工具参数定义必须是对象类型。")
        properties = parameters.get("properties")
        required = parameters.get("required", [])
        if not isinstance(properties, dict) or not isinstance(required, list):
            raise ValueError("工具参数定义必须包含属性说明和必填字段列表。")
        if not set(required).issubset(properties):
            raise ValueError("所有必填字段都必须在属性说明中声明。")
        if parameters.get("additionalProperties") is not False:
            raise ValueError("工具参数定义必须明确禁止未声明的字段。")
        for field, definition in properties.items():
            if (
                not isinstance(definition, dict)
                or definition.get("type") not in _JSON_TYPES
            ):
                raise ValueError(f"字段使用了不支持的数据类型：{field}")
        # 名称唯一，供后续模型描述生成和白名单分发使用。
        self._tools[name] = Tool(name, description, parameters, handler)

    def openai_tools(self) -> list[dict[str, Any]]:
        # 将已登记工具转换成模型接口兼容的函数调用描述格式。
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in self._tools.values()
        ]

    def call(self, name: str, arguments: str | Mapping[str, Any]) -> str:
        # 先按名称检查允许列表，绝不根据模型输出动态导入或执行函数。
        tool = self._tools.get(name)
        if tool is None:
            raise ToolInputError(f"工具未登记：{name}")

        # 模型通常返回 JSON 字符串；本地代码也可以直接传入字典。
        if isinstance(arguments, str):
            try:
                parsed = json.loads(arguments)
            except json.JSONDecodeError as error:
                raise ToolInputError("工具参数必须是有效的 JSON。") from error
        else:
            parsed = arguments
        if not isinstance(parsed, Mapping):
            raise ToolInputError("工具参数必须是 JSON 对象。")

        # 检查必填字段、未声明字段以及每个参数的数据类型。
        properties = tool.parameters["properties"]
        required = tool.parameters.get("required", [])
        missing = set(required) - parsed.keys()
        extra = parsed.keys() - properties.keys()
        if missing:
            raise ToolInputError(f"缺少必填参数：{', '.join(sorted(missing))}")
        if extra:
            raise ToolInputError(f"包含未声明的参数：{', '.join(sorted(extra))}")
        for field, value in parsed.items():
            expected_type = properties[field]["type"]
            if not _JSON_TYPES[expected_type](value):
                raise ToolInputError(f"参数“{field}”必须是{_TYPE_NAMES[expected_type]}类型。")

        # 只有全部参数校验通过后才执行工具，并检查结果是否为文本。
        result = tool.handler(dict(parsed))
        if not isinstance(result, str):
            raise TypeError(f"工具“{name}”必须返回文本结果。")
        return result


def _search_knowledge(arguments: dict[str, Any]) -> str:
    # 使用本地教学知识库按关键词匹配，不访问外部服务。
    knowledge = {
        "智能体": "智能体可以根据目标选择行动并调用工具推进任务。",
        "工作流": "工作流按照预先定义的步骤和控制逻辑执行任务。",
    }
    query = arguments["查询内容"].lower()
    matches = [text for key, text in knowledge.items() if key in query]
    return "\n".join(matches) if matches else "知识库中没有找到匹配内容。"


def _get_product_info(arguments: dict[str, Any]) -> str:
    # 使用固定产品数据演示工具查询，未知名称会返回未找到提示。
    products = {
        "智能体平台": "支持接入模型、调用工具和编排工作流。",
        "知识库系统": "支持导入文档、检索内容和回答问题。",
    }
    return products.get(arguments["产品名称"], "没有找到对应的产品信息。")


def create_registry() -> ToolRegistry:
    # 集中登记工具及其参数定义，供示例和智能体共用。
    registry = ToolRegistry()
    # 函数名称遵循接口格式；参数说明和示例内容使用中文。
    registry.register(
        "search_knowledge",
        "在本地教学知识库中搜索内容。",
        {
            "type": "object",
            "properties": {"查询内容": {"type": "string"}},
            "required": ["查询内容"],
            "additionalProperties": False,
        },
        _search_knowledge,
    )
    registry.register(
        "get_product_info",
        "查询教学用产品说明。",
        {
            "type": "object",
            "properties": {"产品名称": {"type": "string"}},
            "required": ["产品名称"],
            "additionalProperties": False,
        },
        _get_product_info,
    )
    return registry


if __name__ == "__main__":
    # 直接运行时分别演示字典参数和 JSON 字符串参数。
    tools = create_registry()
    print(tools.call("search_knowledge", {"查询内容": "请介绍智能体。"}))
    print(tools.call("get_product_info", '{"产品名称":"智能体平台"}'))
