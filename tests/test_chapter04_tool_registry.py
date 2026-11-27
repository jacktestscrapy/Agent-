"""验证第4章工具注册表与函数调用流程。"""

import unittest
from types import SimpleNamespace

# 导入智能体流程和注册表，用模拟模型响应进行离线测试。
from examples.chapter04.function_calling_agent import run_agent
from examples.chapter04.tool_registry import ToolRegistry, create_registry


class FakeCompletions:
    # 模拟模型 API，按顺序返回预设响应并保留请求供断言检查。
    def __init__(self, messages):
        self.messages = iter(messages)
        self.requests = []

    def create(self, **request):
        self.requests.append(request)
        message = next(self.messages)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeMessage:
    # 提供智能体测试所需的模型消息字段和序列化行为。
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []

    def model_dump(self, exclude_none=True):
        call = self.tool_calls[0]
        return {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
            ],
        }


class ToolRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        # 每个用例使用独立的默认注册表。
        self.registry = create_registry()

    def test_calls_registered_tool_with_dict_or_json_arguments(self) -> None:
        # 验证注册工具接受已解析字典和模型返回的 JSON 字符串。
        self.assertIn(
            "智能体可以根据目标选择行动",
            self.registry.call("search_knowledge", {"查询内容": "请介绍智能体。"}),
        )
        self.assertIn(
            "支持接入模型",
            self.registry.call(
                "get_product_info",
                '{"产品名称":"智能体平台"}',
            ),
        )

    def test_rejects_unknown_tool_and_invalid_arguments(self) -> None:
        # 未登记工具及缺失、多余、类型错误的参数都必须被拒绝。
        with self.assertRaisesRegex(ValueError, "工具未登记"):
            self.registry.call("run_command", {})
        with self.assertRaisesRegex(ValueError, "缺少必填参数"):
            self.registry.call("search_knowledge", {})
        with self.assertRaisesRegex(ValueError, "未声明的参数"):
            self.registry.call("search_knowledge", {"查询内容": "智能体", "额外参数": True})
        with self.assertRaisesRegex(ValueError, "必须是文本类型"):
            self.registry.call("search_knowledge", {"查询内容": 42})

    def test_rejects_duplicate_registration(self) -> None:
        # 工具名必须唯一，避免后续注册覆盖已审核的执行器。
        registry = ToolRegistry()
        parameters = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }
        registry.register("lookup", "查询本地数据。", parameters, lambda _: "正常结果")
        with self.assertRaisesRegex(ValueError, "工具已经登记"):
            registry.register("lookup", "重复登记。", parameters, lambda _: "错误结果")

    def test_function_calling_executes_registered_tool_and_returns_tool_result(self) -> None:
        # 模拟一次工具请求和一次最终回答，检查结果按调用编号回传。
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(
                name="search_knowledge",
                arguments='{"查询内容":"请介绍智能体。"}',
            ),
        )
        completions = FakeCompletions(
            [
                FakeMessage(tool_calls=[tool_call]),
                FakeMessage(content="智能体可以根据目标选择行动并调用工具。"),
            ]
        )
        client = SimpleNamespace(
            chat=SimpleNamespace(completions=completions),
        )

        answer = run_agent("请介绍智能体。", client, "测试模型", self.registry)

        self.assertIn("智能体可以根据目标选择行动", answer)
        self.assertEqual(completions.requests[1]["messages"][-1]["tool_call_id"], "call-1")

    def test_function_calling_does_not_hide_tool_execution_errors(self) -> None:
        # 工具本身的运行错误不应被当作参数校验错误吞掉。
        def broken_tool(_: dict[str, object]) -> str:
            raise RuntimeError("服务暂时不可用")

        registry = ToolRegistry()
        registry.register(
            "failing_tool",
            "用于测试失败情况的工具。",
            {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            broken_tool,
        )
        tool_call = SimpleNamespace(
            id="call-2",
            function=SimpleNamespace(name="failing_tool", arguments="{}"),
        )
        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=FakeCompletions([FakeMessage(tool_calls=[tool_call])]),
            ),
        )

        with self.assertRaisesRegex(RuntimeError, "服务暂时不可用"):
            run_agent("请调用工具。", client, "测试模型", registry)


if __name__ == "__main__":
    # 支持直接运行本测试文件。
    unittest.main()
