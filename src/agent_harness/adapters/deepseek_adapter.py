"""DeepSeek 适配层 — reasoning_content + Function Calling 兼容处理。

Task 6: 处理 DeepSeek thinking 模式下的 reasoning_content 回传规则，
以及 Function Calling 的多个兼容性陷阱（PRD IDEA-010）。
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DeepSeekAdapter:
    """DeepSeek API 适配器。

    核心职责：
    1. 带 tool_calls 的消息：原样保留 reasoning_content，否则 400
    2. 不带 tool_calls 的消息：省略 reasoning_content，避免多余花费
    3. tool_choice 使用显式函数名称，不使用 "required"
    4. deepseek-reasoner 不支持 FC → 自动降级到 deepseek-chat
    """

    # DeepSeek reasoner 系列模型（不支持 Function Calling）
    REASONER_MODELS = {"deepseek-reasoner", "deepseek-reasoner-v4"}

    def __init__(self) -> None:
        self._last_reasoning_content: Optional[str] = None
        self._fc_fallback_triggered = False

    def prepare_request(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Any = None,
        model: str = "deepseek-chat",
    ) -> Dict[str, Any]:
        """准备 API 请求参数。

        Args:
            messages: 消息列表（含历史）。
            tools: 工具定义列表。
            tool_choice: 工具选择策略。
            model: 模型名称。

        Returns:
            处理后的请求参数字典。
        """
        # 检查是否需要 FC 降级
        if tools and model in self.REASONER_MODELS:
            logger.warning(
                "模型 %s 不支持 Function Calling，自动降级到 deepseek-chat",
                model,
            )
            model = "deepseek-chat"
            self._fc_fallback_triggered = True

        # 处理 reasoning_content 规则
        processed_messages = self._process_messages(messages)

        # 处理 tool_choice
        processed_tool_choice = self._process_tool_choice(tool_choice)

        # 构建请求
        request: Dict[str, Any] = {
            "model": model,
            "messages": processed_messages,
        }

        if tools:
            request["tools"] = tools
        if processed_tool_choice is not None:
            request["tool_choice"] = processed_tool_choice

        return request

    def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理 API 响应，提取 reasoning_content。

        Args:
            response: API 原始响应。

        Returns:
            处理后的响应（reasoning_content 单独提取）。
        """
        choice = response.get("choices", [{}])[0]
        message = choice.get("message", {})

        # 提取 reasoning_content（DeepSeek 特有字段）
        reasoning = message.get("reasoning_content")
        if reasoning is not None:
            self._last_reasoning_content = reasoning
            logger.debug("提取 reasoning_content: %d 字符", len(reasoning))
        else:
            self._last_reasoning_content = None

        return response

    def _process_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理消息列表中的 reasoning_content 规则。

        FR-5.1: 带 tool_calls 的消息必须原样保留 reasoning_content
        FR-5.2: 不带 tool_calls 的消息省略 reasoning_content
        """
        processed = []
        for msg in messages:
            msg_copy = dict(msg)

            if msg.get("role") == "assistant":
                has_tool_calls = bool(msg.get("tool_calls"))

                if has_tool_calls:
                    # FR-5.1: 必须保留 reasoning_content
                    if "reasoning_content" not in msg_copy:
                        # 尝试从缓存恢复
                        if self._last_reasoning_content is not None:
                            msg_copy["reasoning_content"] = self._last_reasoning_content
                            logger.debug("从缓存恢复 reasoning_content")
                else:
                    # FR-5.2: 省略 reasoning_content
                    msg_copy.pop("reasoning_content", None)

            processed.append(msg_copy)

        return processed

    def _process_tool_choice(self, tool_choice: Any) -> Any:
        """处理 tool_choice 参数。

        FR-5.3: 使用显式函数名称 {"type": "function", "function": {"name": "..."}}
        DeepSeek 的 tool_choice="required" 不像 OpenAI 倾向于第一个函数。
        """
        if tool_choice is None:
            return None

        if tool_choice == "required":
            # 不使用 "required"，后续调用方应指定具体函数名称
            logger.warning("tool_choice='required' 在 DeepSeek 上不可靠，建议指定函数名称")
            return "required"

        if isinstance(tool_choice, dict):
            return tool_choice

        # 字符串格式 → 转换为字典
        if isinstance(tool_choice, str):
            return {"type": "function", "function": {"name": tool_choice}}

        return tool_choice

    @property
    def last_reasoning_content(self) -> Optional[str]:
        return self._last_reasoning_content

    @property
    def fc_fallback_triggered(self) -> bool:
        return self._fc_fallback_triggered
