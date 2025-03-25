import asyncio
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiohttp
import websockets

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)


async def create_writing_session(session_id: str, topic: str) -> bool:
    """创建写作会话"""
    async with aiohttp.ClientSession() as session:
        try:
            url = "http://localhost:8081/api/ai-assistant/sessions"
            headers = {
                "Authorization": "Bearer test_token"
            }
            data = {
                "article_id": None,
                "initial_stage": "outline",
                "context": {
                    "title": topic,
                    "content": "",
                    "tags": ["python", "tutorial"],
                    "target_length": 2000
                }
            }

            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    print("会话创建成功:", result)
                    return True
                else:
                    print(f"创建会话失败: {response.status}")
                    return False
        except Exception as e:
            print(f"创建会话时出错: {str(e)}")
            return False


async def test_writing_assistant():
    """测试写作助手 WebSocket 连接"""
    # 创建会话ID
    session_id = str(uuid.uuid4())
    topic = "Python异步编程最佳实践"

    # 首先创建HTTP会话
    session_created = await create_writing_session(session_id, topic)
    if not session_created:
        print("无法创建写作会话，测试终止")
        return

    # 连接 WebSocket
    uri = f"ws://localhost:8081/api/ai-assistant/sessions/{session_id}/realtime"
    headers = {
        "Authorization": "Bearer test_token"
    }

    try:
        async with websockets.connect(uri, extra_headers=headers) as websocket:
            print("已连接到写作助手服务器")

            # 测试各种写作功能
            test_cases = [
                {
                    "type": "generate_outline",
                    "data": {},
                    "description": "生成文章大纲"
                },
                {
                    "type": "generate_content",
                    "data": {"section_id": "introduction"},
                    "description": "生成引言部分内容"
                },
                {
                    "type": "optimize_content",
                    "data": {
                        "content": "Python的异步编程是一个重要的主题。通过使用异步编程，"
                                "我们可以提高程序的性能和响应速度。本文将介绍Python异步编程的最佳实践。"
                    },
                    "description": "优化内容"
                },
                {
                    "type": "analyze_content",
                    "data": {
                        "content": "Python的异步编程是一个重要的主题。"
                    },
                    "description": "分析内容"
                },
                {
                    "type": "get_suggestions",
                    "data": {
                        "content": "Python的异步编程是一个重要的主题。"
                    },
                    "description": "获取写作建议"
                }
            ]

            for test_case in test_cases:
                print(f"\n测试: {test_case['description']}")
                # 发送请求
                await websocket.send(json.dumps({
                    "type": test_case["type"],
                    "data": test_case["data"],
                    "timestamp": datetime.utcnow().isoformat()
                }))

                # 接收响应
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    response_data = json.loads(response)
                    print(f"收到响应:")
                    print(json.dumps(response_data, ensure_ascii=False, indent=2))
                except asyncio.TimeoutError:
                    print(f"等待响应超时")
                except Exception as e:
                    print(f"处理响应时出错: {str(e)}")

                # 在请求之间添加短暂延迟
                await asyncio.sleep(1)

    except websockets.exceptions.ConnectionClosed as e:
        print(f"WebSocket连接已关闭: {str(e)}")
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_writing_assistant())
