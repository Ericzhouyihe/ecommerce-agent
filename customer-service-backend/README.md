# customer-service-backend

电商智能客服后端:基于「任务流(Task Flow)」的多轮对话引擎,DDD 四层结构。

## 架构

```text
api                  # 接口层:路由、请求/响应模型、与领域对象的双向映射
 ├─ v1/              # 版本化路由(chat)
application          # 应用层:用例编排(加载状态 → 引擎处理 → 保存状态)+ 组合根(builder)
domain               # 领域层:纯业务逻辑,不依赖框架与基础设施实现
 ├─ dialogue/        # 对话核心:引擎、状态聚合根、会话/轮次、规划器(planner)
 ├─ clarify/         # 澄清应答:计划校验失败时向用户追问
 ├─ chitchat/        # 闲聊轨道
 ├─ knowledge/       # 知识问答轨道:意图 → 知识源(provider) → 生成回复
 └─ task/            # 业务任务轨道:命令处理 + 流程执行 + 动作注册
infrastructure       # 基础设施层:LLM、HTTP 客户端、MySQL(SQLAlchemy)
prompts/             # jinja2 提示词模板与历史构建器
flow_config/         # YAML 流程定义(user_flows + system_flows)
```

依赖方向:`api → application → domain ← infrastructure`(领域层定义 Repository 契约,基础设施实现它,依赖倒置)。

## 一条消息的完整链路

```text
POST /api/chat
  → api: ChatRequest → UserMessage(mappers)
  → application: DialogueService.process_message
      1. repository.load_state(sender_id)      # MySQL 读回整个 DialogueState
      2. engine.process_message(state, msg)
          ├─ 会话管理:超时 1h 自动开新会话并重置运行时状态
          ├─ 文本消息:
          │   ├─ TurnPlanner(LLM) → TurnPlan{task | knowledge | chitchat}
          │   ├─ TurnPlanValidator → 不合法则 ClarifyResponder 澄清追问
          │   └─ 合法 → TaskHandler / KnowledgeHandler / ChitchatHandler
          └─ 对象消息:按当前 collect 槽位匹配 → SetSlotsCommand(免打字填槽)
      3. repository.save_state(state)          # 整体覆盖持久化
  → api: ProcessResult → ChatResponse(mappers)
```

## 任务轨道内部(核心)

```text
CommandProcessor(状态迁移:启动/挂起/恢复/取消任务 + 系统通知流程)
  → FlowExecutor(推进 YAML 流程直到遇到 action_listen 或可执行 action)
      → ActionRunner(注册表分发:action_response / 自定义 API action)
```

- **系统任务优先**:`state.current_task()` 永远先返回系统任务,用于"通知/收集"等旁路流程
- **槽位收集**:collect 步骤无值时激活 `system_collect_information` 子流程提问并挂起主流程,用户回复后 `set_slots` 恢复推进
- **任务挂起/恢复**:新业务插队时旧任务进 `paused_tasks`,之后可通过 `resume_flow` 恢复

## 本地运行

```bash
# 1. 启动 MySQL(docker/mysql/initdb 会自动建库建表并写入演示数据)
docker compose up -d mysql

# 2. 配置 .env(参考 .env.example)
#    必填:LLM_API_KEY;数据库默认与 docker-compose.yml 一致
cp .env.example .env

# 3. 若需手动建表(仅创建缺失的表,不会改已有表结构)
uv run python -m shop_agent.infrastructure.db.init_db

# 4. 启动(依赖本地商城 API,默认 http://127.0.0.1:18081)
uv run python main.py
```

接口文档:`http://127.0.0.1:18082/docs`

## 前端

```bash
cd ../customer-service-frontend
npm ci
npm run dev     # http://127.0.0.1:5173,已代理 /api 与 /commerce
```
