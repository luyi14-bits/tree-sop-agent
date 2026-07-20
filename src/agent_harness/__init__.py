# Tree-SOP Agent — Skill → Agent 自动映射引擎
#
# SPDX-License-Identifier: AGPL-3.0-only

"""Tree-SOP Agent: 将结构化 skill 定义自动映射为独立 AI Agent 的引擎。

核心组件:
- SkillRegistry: 加载和注册 skill 定义
- AgentFactory: 从 skill 定义创建 Agent 实例
- ModelRouter: Pro/Flash 双模型路由
- DeepSeekAdapter: reasoning_content + Function Calling 适配
- CacheEngine: 缓存前缀组装 + 诊断
- ContextPartitioner: 三层上下文分区
- SequentialOrchestrator / HierarchicalOrchestrator: SOP 编排
"""

from .core.skill_def import SkillDef, AgentConfig, SessionConfig, SOPNode, ToolDecl
from .core.skill_parser import SkillParser
from .core.skill_registry import SkillRegistry
from .core.agent_factory import AgentFactory, Agent

__all__ = [
    "SkillDef",
    "AgentConfig",
    "SessionConfig",
    "SOPNode",
    "ToolDecl",
    "SkillParser",
    "SkillRegistry",
    "AgentFactory",
    "Agent",
]
