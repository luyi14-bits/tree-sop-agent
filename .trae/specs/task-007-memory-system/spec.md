# IDEA-022: Memory 体系重构 Spec

## RQ-LOCAL-001: SQLite LocalStore
- **WHEN** MemoryManager 初始化
- **THEN** 创建 SQLite 数据库（profiles/sessions/memory_log 三表）
- **Scenario**: 初始化后三个表都存在

## RQ-ROUTER-001: MemoryRouter 分层路由
- **WHEN** 需要存储记忆
- **THEN** 按类型路由到对应层
- **Scenario**: summary 类型走 ConversationCompressor, episodic 走 SQLite

## RQ-SUMMARY-001: Flash LLM 摘要升级
- **WHEN** ConversationCompressor 触发摘要
- **THEN** 调用 DeepSeek Flash 做真实摘要（离线降级保留）
- **Scenario**: 离线模式仍能产出摘要字符串

## RQ-INDEX-001: EmbeddingIndex 对话记忆
- **WHEN** 调用 add_conversation(text)
- **THEN** 对话记忆与 skill 索引共存
- **Scenario**: search() 同时返回 skill 和 conversation 结果
