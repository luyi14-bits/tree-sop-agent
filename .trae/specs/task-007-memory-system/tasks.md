# Tasks — IDEA-022

- [ ] Task 1: LocalStore SQLite
  - [ ] 三表创建（profiles/sessions/memory_log）
  - [ ] CRUD 操作
  - [ ] 测试

- [ ] Task 2: MemoryRouter
  - [ ] working 路由 → ContextPartitioner
  - [ ] summary 路由 → ConversationCompressor
  - [ ] episodic 路由 → SQLite
  - [ ] semantic 路由 → EmbeddingIndex

- [ ] Task 3: ConversationCompressor Flash 升级
  - [ ] _make_summary 改为 Flash 调用
  - [ ] 离线降级保留

- [ ] Task 4: EmbeddingIndex 对话记忆
  - [ ] add_conversation()
  - [ ] 双索引混合排序

- [ ] Task 5: Consolidator
  - [ ] forget() — 基于访问频率评分
  - [ ] merge() — 相似摘要合并

# Dependencies
- Task 1 无依赖（基础设施）
- Task 2 depends on Task 1
- Task 3 无依赖
- Task 4 无依赖
- Task 5 depends on Task 2

# 工时
| Task | 人天 |
|:----:|:----:|
| 1 | 0.5 |
| 2 | 0.5 |
| 3 | 0.25 |
| 4 | 0.25 |
| 5 | 0.25 |
| **合计** | **1.75** |
