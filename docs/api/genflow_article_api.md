```markdown
# GenFlow 文章系统 API

## 1. 概述

GenFlow 文章系统提供了完整的文章管理功能，包括创建、编辑、发布、查询等操作。本文档描述了文章系统的 API 接口规范。

## 2. 基础信息

- 基础路径：`/api/articles`
- 所有请求需要包含标准请求头
- 所有响应遵循统一的响应格式

### 2.1 标准请求头
```http
Content-Type: application/json
Accept: application/json
X-Request-ID: <uuid>
X-Client-Version: <version>
Authorization: Bearer <token>
```

## 3. API 端点

### 3.1 创建文章

#### 请求
- 方法：`POST`
- 路径：`/api/articles`
- 需要认证：是
- 内容类型：`application/json`

```json
{
  "title": "文章标题",
  "content": "文章内容",
  "summary": "文章摘要",
  "cover_image": "封面图片URL",
  "tags": ["标签1", "标签2"]
}
```

#### 成功响应
- 状态码：`201 Created`
```json
{
  "data": {
    "id": "article_123",
    "title": "文章标题",
    "content": "文章内容",
    "summary": "文章摘要",
    "cover_image": "封面图片URL",
    "status": "draft",
    "author_id": "user_123",
    "author": {
      "id": "user_123",
      "name": "作者名称",
      "avatar": "头像URL"
    },
    "created_at": "2024-03-24T10:30:00Z",
    "updated_at": "2024-03-24T10:30:00Z",
    "published_at": null,
    "view_count": 0,
    "tags": ["标签1", "标签2"]
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

### 3.2 获取文章列表

#### 请求
- 方法：`GET`
- 路径：`/api/articles`
- 需要认证：是
- 查询参数：
  - `page`: 页码（默认：1）
  - `per_page`: 每页数量（默认：10）
  - `status`: 文章状态（可选：draft, published）
  - `tags`: 标签筛选（可多选）
  - `created_after`: 创建时间起始
  - `created_before`: 创建时间结束

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": [{
    "id": "article_123",
    "title": "文章标题",
    "summary": "文章摘要",
    "cover_image": "封面图片URL",
    "status": "published",
    "author": {
      "id": "user_123",
      "name": "作者名称"
    },
    "created_at": "2024-03-24T10:30:00Z",
    "published_at": "2024-03-24T11:00:00Z",
    "view_count": 100,
    "tags": ["标签1", "标签2"]
  }],
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc",
    "page": 1,
    "pageSize": 10,
    "total": 100,
    "totalPages": 10
  }
}
```

### 3.3 获取文章详情

#### 请求
- 方法：`GET`
- 路径：`/api/articles/{id}`
- 需要认证：是

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "id": "article_123",
    "title": "文章标题",
    "content": "文章内容",
    "summary": "文章摘要",
    "cover_image": "封面图片URL",
    "status": "published",
    "author_id": "user_123",
    "author": {
      "id": "user_123",
      "name": "作者名称",
      "avatar": "头像URL"
    },
    "created_at": "2024-03-24T10:30:00Z",
    "updated_at": "2024-03-24T10:30:00Z",
    "published_at": "2024-03-24T11:00:00Z",
    "view_count": 100,
    "tags": ["标签1", "标签2"]
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

### 3.4 更新文章

#### 请求
- 方法：`PUT`
- 路径：`/api/articles/{id}`
- 需要认证：是
- 内容类型：`application/json`

```json
{
  "title": "更新的标题",
  "content": "更新的内容",
  "summary": "更新的摘要",
  "cover_image": "新的封面图片URL",
  "tags": ["新标签1", "新标签2"]
}
```

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "id": "article_123",
    "title": "更新的标题",
    "content": "更新的内容",
    "summary": "更新的摘要",
    "cover_image": "新的封面图片URL",
    "status": "draft",
    "updated_at": "2024-03-24T12:30:00Z",
    "tags": ["新标签1", "新标签2"]
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

### 3.5 发布文章

#### 请求
- 方法：`POST`
- 路径：`/api/articles/{id}/publish`
- 需要认证：是

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "id": "article_123",
    "status": "published",
    "published_at": "2024-03-24T12:30:00Z"
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

### 3.6 删除文章

#### 请求
- 方法：`DELETE`
- 路径：`/api/articles/{id}`
- 需要认证：是

#### 成功响应
- 状态码：`204 No Content`

## 4. 错误代码

| 错误代码 | HTTP 状态码 | 描述 |
|----------|------------|------|
| RES_001 | 404 | 文章不存在 |
| RES_002 | 409 | 资源冲突（如重复发布） |
| RES_003 | 403 | 无权限操作此文章 |
| REQ_001 | 400 | 无效的请求格式 |
| REQ_002 | 400 | 缺少必要参数 |
| REQ_003 | 400 | 参数格式错误 |
| AUTH_001 | 401 | 未认证 |
| AUTH_004 | 403 | 权限不足 |

## 5. 安全措施

### 5.1 访问控制
- 所有请求必须包含有效的认证令牌
- 只有作者本人或管理员可以编辑/删除文章
- 已发布文章的部分字段不可修改

### 5.2 请求安全
- 所有请求必须使用 HTTPS
- 实现 CSRF 保护
- 请求参数验证和清理
- 适当的 CORS 策略

### 5.3 速率限制
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1616789000
```

## 6. 数据验证规则

### 6.1 字段验证
```typescript
interface ArticleValidation {
  title: {
    required: true,
    minLength: 2,
    maxLength: 100
  },
  content: {
    required: true,
    minLength: 10,
    maxLength: 50000
  },
  summary: {
    required: false,
    maxLength: 200
  },
  tags: {
    required: false,
    maxItems: 5,
    itemMaxLength: 20
  }
}
```

## 7. 性能优化

### 7.1 响应字段筛选
- 支持通过 `fields` 参数指定返回字段
- 示例：`?fields=id,title,summary`

### 7.2 缓存策略
- 已发布文章默认缓存 5 分钟
- 支持条件请求：`If-None-Match`、`If-Modified-Since`

---

最后更新: 2024-03-24
```
