# 控制AI 使用文档

## 1. 概述

控制AI是GenFlow内容生产系统的智能控制中心，提供自然语言理解和命令式接口的统一处理，连接用户与专业团队（选题、研究、写作、风格和审核），实现内容创作全流程的智能协调。

### 主要功能

- **自然语言理解**：将用户的自然语言请求转换为结构化任务
- **意图识别**：识别用户意图，提取关键实体信息
- **任务规划**：规划任务执行流程，确定调用的团队和顺序
- **执行协调**：协调各专业团队完成内容生产任务
- **状态管理**：维护会话状态，保持上下文连贯性
- **多模态交互**：支持HTTP和WebSocket两种通信方式

### 系统架构

控制AI包含以下核心组件：

1. **ControlAI类**：核心控制AI逻辑，实现自然语言处理和任务规划
2. **API模块**：提供HTTP和WebSocket接口，支持同步和异步交互
3. **客户端模块**：与各专业团队API交互的客户端，执行具体任务

## 2. 安装与配置

### 环境要求

- Python 3.8+
- OpenAI API密钥
- 各专业团队服务已启动并可访问

### 安装步骤

1. 确保已安装所有依赖包：

```bash
pip install -r requirements.txt
```

2. 设置环境变量：

```bash
# 设置OpenAI API密钥
export OPENAI_API_KEY="your-api-key"

# 设置OpenAI模型（可选，默认为gpt-4-turbo-preview）
export OPENAI_MODEL="gpt-4"

# 设置各团队API地址（可选，有默认值）
export TOPIC_API_URL="http://localhost:8001/api/v1/topic"
export RESEARCH_API_URL="http://localhost:8002/api/v1/research"
export WRITING_API_URL="http://localhost:8003/api/v1/writing"
export STYLE_API_URL="http://localhost:8004/api/v1/style"
export REVIEW_API_URL="http://localhost:8005/api/v1/review"
```

### 配置文件

在`core/control_ai/config/`目录中包含以下配置文件：

- `system_prompt.txt`：系统提示词，定义控制AI的行为和能力

## 3. API接口

控制AI提供REST API和WebSocket两种接口。

### REST API接口

#### 1. 处理自然语言请求

```
POST /api/v1/nl/process
```

请求体：
```json
{
  "query": "写一篇关于AI发展的文章",
  "session_id": "optional-session-id"
}
```

响应：
```json
{
  "success": true,
  "message": "请求处理成功",
  "data": {
    "response": "我将帮您创建一篇关于AI发展的深度分析文章。我需要先收集相关资料，然后进行撰写，预计需要3分钟完成。需要特别关注某些方面吗？",
    "next_actions": [
      {"type": "proceed", "name": "开始", "description": "开始执行计划的任务"},
      {"type": "refine", "name": "调整", "description": "调整任务参数"},
      {"type": "cancel", "name": "取消", "description": "取消当前任务"}
    ],
    "intent": {...},
    "task_plan": {...}
  },
  "session_id": "generated-or-provided-session-id",
  "timestamp": "2023-07-01T12:00:00.000Z"
}
```

#### 2. 执行任务

```
POST /api/v1/task/execute
```

请求体：
```json
{
  "session_id": "your-session-id",
  "action": "proceed",
  "parameters": {} // 可选参数
}
```

响应：
```json
{
  "success": true,
  "message": "任务已开始执行",
  "data": {
    "task_plan": {...},
    "estimated_time": 180
  },
  "session_id": "your-session-id",
  "timestamp": "2023-07-01T12:01:00.000Z"
}
```

#### 3. 获取会话信息

```
GET /api/v1/session/{session_id}
```

响应：
```json
{
  "success": true,
  "message": "会话信息获取成功",
  "data": {
    "session": {...}
  },
  "session_id": "your-session-id",
  "timestamp": "2023-07-01T12:02:00.000Z"
}
```

### WebSocket接口

连接地址：`ws://your-host/ws/{session_id}`

#### 1. 发送自然语言请求

```json
{
  "type": "nl_request",
  "query": "写一篇关于AI发展的文章"
}
```

#### 2. 执行任务

```json
{
  "type": "execute_task",
  "action": "proceed",
  "parameters": {}
}
```

#### 3. 心跳检测

```json
{
  "type": "ping"
}
```

#### 服务器推送消息类型

- `connected`：连接成功
- `session_created`：会话创建成功
- `nl_response`：自然语言处理响应
- `task_started`：任务开始执行
- `step_started`：任务步骤开始执行
- `step_completed`：任务步骤完成
- `step_failed`：任务步骤失败
- `task_completed`：任务全部完成
- `task_summary`：任务执行总结
- `task_cancelled`：任务被取消
- `error`：发生错误
- `pong`：心跳响应

## 4. 使用示例

### 使用REST API

```python
import requests
import json

# 1. 处理自然语言请求
response = requests.post(
    "http://localhost:8000/api/v1/nl/process",
    json={"query": "写一篇关于量子计算的科普文章"}
)
result = response.json()
session_id = result["session_id"]

# 2. 执行任务
response = requests.post(
    "http://localhost:8000/api/v1/task/execute",
    json={"session_id": session_id, "action": "proceed"}
)

# 3. 获取会话信息
response = requests.get(f"http://localhost:8000/api/v1/session/{session_id}")
session_info = response.json()
```

### 使用WebSocket

```python
import asyncio
import websockets
import json

async def interact_with_control_ai():
    uri = "ws://localhost:8000/ws/my-session"

    async with websockets.connect(uri) as websocket:
        # 1. 接收连接成功消息
        response = await websocket.recv()
        print(f"连接响应: {response}")

        # 2. 发送自然语言请求
        await websocket.send(json.dumps({
            "type": "nl_request",
            "query": "写一篇关于量子计算的科普文章"
        }))

        # 3. 接收响应
        response = await websocket.recv()
        print(f"NL响应: {response}")

        # 4. 执行任务
        await websocket.send(json.dumps({
            "type": "execute_task",
            "action": "proceed"
        }))

        # 5. 持续接收任务执行状态
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"任务状态: {response_data['type']}")

            # 如果任务完成，退出循环
            if response_data["type"] == "task_summary":
                break

# 运行WebSocket客户端
asyncio.run(interact_with_control_ai())
```

## 5. 支持的意图类型

控制AI支持以下类型的用户意图：

1. **trending_query**: 查询热门话题
   - 例："帮我找一些今天的热门话题"，"有什么值得写的科技话题"

2. **research_request**: 研究特定话题
   - 例："收集关于元宇宙最新发展的资料"，"整理ChatGPT最新应用案例"

3. **writing_request**: 内容创作请求
   - 例："写一篇关于人工智能的文章"，"帮我写个短视频脚本介绍量子计算"

4. **style_request**: 风格调整请求
   - 例："把这段内容改成更幽默的风格"，"调整成适合知乎的专业风格"

5. **review_request**: 审核和修改请求
   - 例："帮我检查这篇文章有没有问题"，"优化这篇文章的结构"

6. **full_content_production**: 完整内容生产流程
   - 例："从选题到成稿，完成一篇关于元宇宙的文章"

## 6. 故障排除

### 常见问题

1. **OpenAI API调用错误**
   - 检查API密钥是否正确设置
   - 检查模型名称是否正确
   - 查看OpenAI服务状态

2. **团队API连接错误**
   - 确保各团队服务已启动
   - 检查API地址配置是否正确
   - 验证网络连接性

3. **会话状态丢失**
   - 会话默认保存在内存中，服务重启会丢失
   - 考虑实现持久化存储如Redis或数据库

### 日志说明

控制AI使用Python标准日志库，日志级别默认为INFO。主要日志消息包括：

- API请求和响应信息
- 意图识别结果和置信度
- 任务规划和执行状态
- 错误和异常信息

## 7. 开发与扩展

### 添加新的意图类型

1. 在`core/control_ai/control_ai.py`中的`supported_intents`字典添加新意图
2. 在系统提示词中添加新意图的描述和示例
3. 实现相应的任务处理逻辑

### 添加新的任务执行步骤

1. 在`ClientFactory`中添加新团队的客户端实现
2. 在`execute_task_step`方法中添加对新团队的处理

### 改进自然语言理解能力

1. 优化系统提示词
2. 使用微调模型或特定领域的模型
3. 添加用户反馈机制，不断优化模型响应

## 8. 贡献指南

欢迎为控制AI功能提供改进和贡献。请遵循以下步骤：

1. Fork项目仓库
2. 创建功能分支
3. 编写代码并添加测试
4. 提交PR，描述所做的更改

## 9. 版本历史

- v1.0.0 (2023-07-01) - 初始版本，提供基础自然语言理解和任务规划功能
- v1.1.0 (计划中) - 添加持久化存储支持
- v1.2.0 (计划中) - 增强多轮对话能力
