# Skill → Agent 映射引擎 Spec

## Why

当前每个开发迭代需要手动切换 Agent 上下文，缺乏统一的 skill 定义格式和自动映射机制。系统无法自动将 skill 定义转化为独立 Agent，导致：
- 新 skill 需要手动配置 Agent 参数，每次数小时
- DeepSeek Pro/Flash 模型混用无自动化策略，API 成本浪费 60-70%
- 缓存命中率不可控，费用波动大
- Function Calling 在 DeepSeek 上频繁踩坑（400 错误）
- 复杂任务无法拆解为子 Agent 树形协作

## Meta

- **优先级**: P0
- **估算工时**: 4.5 人天（经 Trinity 精简审查，从 40 子任务缩减至 18）
- **影响 Spec**: 无（全新项目）
- **PRD 来源**: `docs/prd/task-001-skill-agent-mapping-prd.md`

---

## What Changes

- **BREAKING** 全新项目，无向后兼容问题
- 创建 `agent_harness/` Python 包，包含 6 大模块
- 定义 Skill frontmatter 格式规范（YAML frontmatter in Markdown）
- 实现 Skill → Agent 映射引擎（加载→解析→实例化）
- 实现 DeepSeek Pro/Flash 双模型策略（独立 session）
- 实现缓存前缀组装引擎（字节级不变性保障）
- 实现 reasoning_content + Function Calling 适配层
- 实现三层 Context 分区架构
- 实现 SOP 编排调度器（顺序/层级/并行）
- 提供独立 CLI 自测脚本 `auto_test.py`
- 提供 pytest 单元测试套件

## Impact

- Affected specs: 无（全新）
- Affected code: 全新 `src/agent_harness/` 目录

---

## Requirements

### Requirement: SKILL-FMT-001
The system SHALL define a structured Markdown + YAML frontmatter format for skill definitions.

#### Scenario: Basic skill definition
- **GIVEN** a new skill file with valid YAML frontmatter
- **WHEN** the system parses it
- **THEN** it extracts name, description, tools, and model fields
- **AND** it validates all required fields are present

#### Scenario: Missing required field
- **GIVEN** a skill file missing the `model` field
- **WHEN** the system parses it
- **THEN** it raises a validation error with the missing field name

---

### Requirement: MAP-ENG-001
The system SHALL automatically generate an Agent instance from a skill definition upon loading.

#### Scenario: Agent auto-creation
- **GIVEN** a valid skill definition file
- **WHEN** `SkillRegistry.load(path)` is called
- **THEN** an Agent instance is created with the skill's role preset
- **AND** the Agent has access to the tools declared in the skill

#### Scenario: Agent isolation
- **GIVEN** two skill definitions loaded into the same process
- **WHEN** both Agents execute concurrently
- **THEN** their contexts SHALL NOT leak between each other
- **AND** each Agent has its own session and memory

---

### Requirement: MODEL-STRAT-001
The system SHALL support Pro/Flash dual-model strategy with independent sessions.

#### Scenario: Pro for planning skills
- **GIVEN** a PM skill with `model: pro` in frontmatter
- **WHEN** the Agent is invoked
- **THEN** it uses DeepSeek V4 Pro (deepseek-chat with reasoning)
- **AND** its session is independent from Flash sessions

#### Scenario: Flash for execution skills
- **GIVEN** a Coding skill with `model: flash` in frontmatter
- **WHEN** the Agent is invoked
- **THEN** it uses DeepSeek V4 Flash (deepseek-chat without reasoning)
- **AND** its session is independent from Pro sessions

---

### Requirement: CACHE-PREFIX-001
The system SHALL assemble the system prompt prefix in a fixed order to ensure byte-level invariance within a session.

#### Scenario: Prefix assembly order
- **GIVEN** a running session
- **WHEN** the system sends an API request
- **THEN** the prefix is assembled as: base prompt → output style → language → memory → skill index (name + description only)
- **AND** skill body content is NOT included in the prefix

#### Scenario: Prefix change detection
- **GIVEN** a session with an established prefix
- **WHEN** a memory update occurs mid-session
- **THEN** the change is appended as `<memory-update>` XML block in the user message
- **AND** the prefix itself remains byte-level unchanged

---

### Requirement: FC-ADAPT-001
The system SHALL handle DeepSeek-specific reasoning_content rules and Function Calling compatibility.

#### Scenario: reasoning_content preservation
- **GIVEN** a previous assistant response with `tool_calls`
- **WHEN** the system sends the next request
- **THEN** it MUST include the exact `reasoning_content` from the previous response
- **OR** the API returns 400

#### Scenario: reasoning_content omission
- **GIVEN** a previous assistant response WITHOUT `tool_calls`
- **WHEN** the system sends the next request
- **THEN** it MUST NOT include `reasoning_content`

#### Scenario: tool_choice explicit naming
- **GIVEN** a request that must use a specific tool
- **WHEN** the system sets `tool_choice`
- **THEN** it MUST use `{"type": "function", "function": {"name": "..."}}` instead of `"required"`
- **AND** it MUST NOT rely on OpenAI-style default to first function

#### Scenario: reasoner mode fallback
- **GIVEN** `deepseek-reasoner` model (V4-Pro thinking mode)
- **WHEN** the system needs Function Calling
- **THEN** it MUST automatically fall back to `deepseek-chat` model
- **AND** log the fallback event

---

### Requirement: CTX-PART-001
The system SHALL partition API context into three zones: immutable prefix, append-only log, volatile scratchpad.

#### Scenario: immutable prefix caching
- **GIVEN** a session with established context
- **WHEN** comparing prefix snapshots across requests
- **THEN** the immutable prefix (system + tools + memory) SHALL be byte-level identical
- **AND** it SHALL hit DeepSeek cache on every request

#### Scenario: volatile scratchpad exclusion
- **GIVEN** the system is performing reasoning or planning
- **WHEN** constructing the API request
- **THEN** the volatile scratchpad (intermediate reasoning, temp plans) SHALL NOT be included

---

### Requirement: SOP-ORCH-001
The system SHALL support sequential, parallel, and hierarchical SOP orchestration modes.

#### Scenario: sequential orchestration
- **GIVEN** an SOP definition with sequential sub-steps
- **WHEN** the orchestrator executes it
- **THEN** each step runs in order
- **AND** step N+1 receives step N's output as context

#### Scenario: hierarchical orchestration
- **GIVEN** an SOP tree with nested sub-SOPs
- **WHEN** the orchestrator executes it
- **THEN** it recursively expands sub-SOPs
- **AND** each level maintains its own context scope

---

### Requirement: CLI-SELF-001
The system SHALL provide a standalone CLI self-test script `auto_test.py`.

#### Scenario: CLI self-test runs
- **GIVEN** the `auto_test.py` script
- **WHEN** invoked from command line
- **THEN** it runs through all self-test cases
- **AND** exits with code 0 on success, 1 on failure
- **AND** prints diagnostic information on failure

---
