# openai-python examples 循序渐进学习路线

**目标**：按难度分层，从入门到进阶系统掌握本仓库 `examples/` 目录中的全部示例。

---

## 准备

```bash
cd ~/github/openai-python
uv sync                              # 安装依赖
export OPENAI_API_KEY="sk-..."       # 注意：千万别提交到 git
# 运行示例：
uv run python examples/demo.py
```

**学习方法**：每个示例文件都很短（大多 25–80 行），先**读代码猜输出 → 运行对照 → 修改参数复跑**，效果最好。

---

## 阶段 1：基础入门（同步 API）

| 文件 | 行数 | 学习点 |
|---|---|---|
| `demo.py` | 53 | 三件事：非流式请求、流式请求（`stream=True` + `for chunk`）、`with_raw_response` 拿响应头/request_id |
| `module_client.py` | 25 | `openai` 模块 vs `OpenAI()` 客户端的区别（模块级 API 是为新手/REPL 设计的） |
| `streaming.py` | 56 | 同步+异步各一份：手动 `next()` vs `for` 循环遍历流式响应 |

**目标**：搞懂"客户端 → create → 响应对象"的基本链路，以及流式和非流式的区别。

## 阶段 2：异步 API

| 文件 | 学习点 |
|---|---|
| `async_demo.py` (30 行) | `AsyncOpenAI` + `await` + `async for`，与 `demo.py` 逐行对照着看 |

## 阶段 3：结构化输出（Pydantic 解析）

| 文件 | 学习点 |
|---|---|
| `parsing.py` (36) | `chat.completions.parse(response_format=MathResponse)`，定义 Pydantic 模型拿结构化结果 |
| `parsing_stream.py` (42) | 结构化输出 + 流式 |
| `parsing_tools.py` (80) | 函数调用（tools）+ parse 组合 |
| `parsing_tools_stream.py` (38) | 上面两者再加流式 |
| `responses/structured_outputs.py` (55) | 同一功能在 **Responses API** 里的写法（`text_format=`） |
| `responses/structured_outputs_tools.py` (73) | Responses API + tools |

## 阶段 4：Responses API（新一代 API）

| 文件 | 学习点 |
|---|---|
| `responses/streaming.py` (30) | 最简 Responses 流式 |
| `responses/streaming_tools.py` (68) | Responses + 工具调用流式 |
| `responses/background.py` / `background_streaming.py` (46/48) | `background` 模式：异步处理长任务 |
| `responses/multi_agent_streaming.py` / `multi_agent_websocket.py` (40/46) | 多 Agent 编排 |
| `responses/websocket.py` (**436**) | **压轴**：完整 WebSocket agent（带库存 SKU 工具、TypedDict 类型定义），前期可以只看框架 |

## 阶段 5：多模态（图像/音频/视频）

| 文件 | 学习点 |
|---|---|
| `audio.py` (38) | 音频输入输出 |
| `image_stream.py` (53) | 图像生成流式（部分图像 `partial_image` 事件，挺有趣） |
| `speech_to_text.py` / `text_to_speech.py` (25/31) | 语音转写 / 语音合成（很短的入门） |
| `video.py` (22) | 视频输入 |
| `picture.py` | 图像理解 |
| `responses_input_tokens.py` (54) | 计费相关的 token 统计 |

## 阶段 6：高级/云服务集成（按需学，不必全看）

| 文件 | 学习点 |
|---|---|
| `uploads.py` (58) | 文件上传 API |
| `azure.py` (43) / `azure_ad.py` (67) | Azure OpenAI 接入 + Entra ID 认证 |
| `bedrock.py` / `bedrock_runtime.py` | AWS Bedrock 接入 |
| `mtls_httpx*.py`、`httpx2_client.py` | 自定义 HTTP 客户端 / mTLS / HTTPX2（对应 README 第 1009 行那节） |
| `x509_workload_identity*.py` | X.509 工作负载身份认证 |

## 阶段 7：Realtime API（语音实时对话，最难）

| 文件 | 学习点 |
|---|---|
| `realtime/realtime.py` (54) | 纯文本 modality，搞清楚连接/会话/消息模型 |
| `realtime/azure_realtime.py` (79) | Azure 版本 |
| `realtime/push_to_talk_app.py` (**294**) | 完整的语音对讲 TUI 应用（配合 `audio_util.py`），最终挑战 |

---

## 学习方法论

1. **成对对照**：仓库里大量 `xxx` / `xxx_async` / `xxx_stream` 成对出现（sync↔async、普通↔流式），对照学习效果翻倍。
2. **结合主 README.md**：README 是按功能组织的文档（Realtime 在第 433 行附近、HTTPX2 在 1009 行附近），示例是文档的"可运行精炼版"。先看示例，卡住再翻对应章节。
3. **建议主线顺序**：阶段 1→2→3→4→7（覆盖 SDK 核心能力）；阶段 5 按兴趣穿插；阶段 6 用到再学。
4. **动手改**：每个示例跑通后，改 model、改 prompt、把 `create` 换成 `parse`，观察报错和差异——这是最快的学习方式。
5. 若没有 API key，可参考 `tests/` 目录里的 mock 用例学习（不花钱），但入门阶段直接跑示例最直观。