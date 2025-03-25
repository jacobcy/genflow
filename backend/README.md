# GenFlow Backend

GenFlow 是一个现代化的 AI 驱动的内容管理系统后端。

## 技术栈

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- Celery
- OpenAI

## 开发环境设置

1. 确保安装了 Python 3.12:
```bash
python3 --version  # 应该显示 3.12.x
```

2. 安装 uv (如果还没有):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. 创建虚拟环境并安装依赖:
```bash
uv venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

4. 设置环境变量:
```bash
cp .env.example .env
# 编辑 .env 文件设置必要的环境变量
```

5. 运行开发服务器:
```bash
uvicorn src.main:app --reload
```

## 项目结构

```
backend/
├── alembic/              # 数据库迁移
├── src/
│   ├── api/             # API 路由
│   ├── core/            # 核心配置
│   ├── models/          # 数据库模型
│   ├── schemas/         # Pydantic 模型
│   ├── services/        # 业务逻辑
│   └── utils/           # 工具函数
├── tests/               # 测试用例
└── docker/              # Docker 配置
```

## 开发工具

- **格式化**: `black .`
- **Lint**: `ruff check .`
- **类型检查**: `mypy .`
- **测试**: `pytest`

## Docker 部署

```bash
docker compose up -d
```

## API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT 