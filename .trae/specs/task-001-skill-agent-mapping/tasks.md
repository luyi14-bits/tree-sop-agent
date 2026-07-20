# Tasks

> 经 Trinity 精简审查：原 40 子任务 → 合并为 18 子任务（55% 削减），人天从 9→4.5。

- [ ] Task 1: 项目骨架与模块结构
  - [ ] 创建 `agent_harness/` 包结构（`__init__.py`、`core/`、`adapters/`、`orchestrator/`、`cli/`）
  - [ ] 设计核心数据模型：SkillDef, AgentConfig, Session, Context, SOPNode
  - [ ] 配置管理模块：`settings.py`（Pydantic BaseSettings → DeepSeek API Key, model mapping）

- [ ] Task 2: Skill 定义格式解析器
  - [ ] 实现 YAML frontmatter 解析器（`skill_parser.py`）
  - [ ] 实现字段验证（name, description, tools, model, sub_skills 等）
  - [ ] 实现树形 SOP 嵌套定义解析（`SOPNode` 递归结构）
  - [ ] 实现工具声明解析（MCP server / shell / API 三种类型）

- [ ] Task 3: Skill → Agent 映射引擎
  - [ ] 实现 `SkillRegistry`：加载 skill → 验证 → 注册到全局注册表
  - [ ] 实现 `AgentFactory`：SkillDef → AgentConfig → Agent 实例化
  - [ ] 实现 `Agent` 类：封装 role preset（system prompt）+ tools + model + session 生命周期
  - [ ] 实现 Agent 间上下文隔离（独立 `ContextStore` 实例）

- [ ] Task 4: DeepSeek 模型策略管理器
  - [ ] 实现 `ModelRouter`：根据 skill frontmatter 的 model 字段路由到 Pro/Flash
  - [ ] 实现 Pro 模型配置（`deepseek-chat` + reasoning 启用）
  - [ ] 实现 Flash 模型配置（`deepseek-chat` + reasoning 禁用）
  - [ ] 实现独立 Session 管理（Pro 和 Flash 各维护独立 session 池）

- [ ] Task 5: 缓存前缀组装引擎
  - [ ] 实现固定顺序前缀组装：base prompt → output style → language → memory → skill index
  - [ ] 实现 `PrefixSnapshot`：每次请求前计算前缀 hash，比对上一轮
  - [ ] 实现 `<memory-update>` XML 块机制：记忆更新不进前缀，走 user message 尾部
  - [ ] 实现 `CacheDiagnostic`：记录 PrefixChanged + PrefixChangeReasons + 命中率统计

- [ ] Task 6: reasoning_content + FC 适配层
  - [ ] 实现 `DeepSeekAdapter`：拦截 API 请求/响应，处理 reasoning_content 规则
  - [ ] 实现 tool_calls 消息的 reasoning_content 保留逻辑
  - [ ] 实现 非 tool_calls 消息的 reasoning_content 省略逻辑
  - [ ] 实现 tool_choice 显式函数名称设定（规避 `"required"` 问题）
  - [ ] 实现 deepseek-reasoner → deepseek-chat 自动降级

- [ ] Task 7: 三层 Context 分区架构
  - [ ] 实现 `ContextPartitioner`：将消息序列分为 immutable / append-only / volatile 三区
  - [ ] 实现 immutable 区：system + tools + memory，整 session 缓存命中
  - [ ] 实现 append-only 区：对话历史，稳定增长尾部 miss
  - [ ] 实现 volatile 区：推理过程、临时计划，不发给 API

- [ ] Task 8: SOP 编排调度器
  - [ ] 实现 `SequentialOrchestrator`：串行执行子 Agent，结果传递
  - [ ] 实现 `HierarchicalOrchestrator`：递归展开树形 SOP，层级上下文隔离
  - [ ] 实现 `ParallelOrchestrator`（P1）：同时执行多个子 Agent
  - [ ] 实现交接包协议：Agent → Agent 的结果传递（`HandoverPackage`）

- [ ] Task 9: CLI 自测脚本
  - [ ] 实现 `auto_test.py`：独立 CLI 脚本，exit(0) 成功 / exit(1) 失败
  - [ ] 实现多策略验证：每策略执行后验证结果，失败自动降级
  - [ ] 实现聚合错误信息：全部策略失败时异常包含所有错误原因

- [ ] Task 10: pytest 单元测试套件
  - [ ] Skill 解析器测试（frontmatter 有效/无效/缺失字段）
  - [ ] Agent 映射测试（加载→注册→实例化全链路）
  - [ ] 模型路由测试（Pro/Flash 分配 + session 隔离）
  - [ ] 缓存前缀测试（字节级不变性 + 变更检测）
  - [ ] FC 适配层测试（reasoning_content 保留/省略/降级）
  - [ ] SOP 编排测试（顺序/层级/并行）

---

# Task Dependencies

- Task 1 无依赖（项目骨架是基础设施）
- Task 2 depends on Task 1（需要包结构和数据模型）
- Task 3 depends on Task 2（映射引擎需要解析器）
- Task 4 depends on Task 1（需要 settings.py 配置管理）
- Task 5 depends on Task 4（缓存引擎需要 model router 的 session 管理）
- Task 6 depends on Task 4（FC 适配层需要 model router）
- Task 7 depends on Task 1 + Task 5（分区架构需要包结构 + 缓存引擎）
- Task 8 depends on Task 3（编排器需要 Agent 工厂）
- Task 9 depends on Task 3 + Task 4 + Task 6（自测脚本需要完整组件就绪）
- Task 10 depends on Task 2 + Task 3 + Task 4 + Task 5 + Task 6 + Task 8（端到端测试需要全部组件就绪）
- Task 3 可以和 Task 4 并行（独立模块，无交叉依赖）
- Task 6 可以和 Task 7 并行（独立模块，无交叉依赖）

---

# 工时估算

| Task | 子任务数 | 估算人天 |
|------|:-------:|:--------:|
| Task 1: 项目骨架 | 3 | 0.25 |
| Task 2: Skill 解析器 | 4 | 0.5 |
| Task 3: 映射引擎 | 4 | 0.75 |
| Task 4: 模型策略 | 4 | 0.5 |
| Task 5: 缓存前缀 | 4 | 0.75 |
| Task 6: FC 适配层 | 5 | 0.75 |
| Task 7: Context 分区 | 4 | 0.5 |
| Task 8: SOP 编排 | 4 | 0.5 |
| Task 9: CLI 自测脚本 | 3 | 0.25 |
| Task 10: pytest 套件 | 6 | 0.75 |
| **合计** | **41** | **4.5 人天** |
