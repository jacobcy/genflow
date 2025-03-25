# GenFlow 认证系统 API

## 1. 概述

GenFlow 使用基于 JWT 的认证系统，支持用户和管理员两种角色的访问控制。本文档描述了认证系统的 API 接口规范。

## 2. 基础信息

- 基础路径：`/api/auth`
- 所有请求都需要包含标准请求头
- 所有响应都遵循统一的响应格式

### 2.1 标准请求头
```http
Content-Type: application/json
Accept: application/json
X-Request-ID: <uuid>
X-Client-Version: <version>
```

### 2.2 认证头格式
```http
Authorization: Bearer <token>
```

## 3. API 端点

### 3.1 登录

#### 请求
- 方法：`POST`
- 路径：`/api/auth/login`
- 内容类型：`application/json`

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "tokens": {
      "accessToken": {
        "token": "eyJhbG...",
        "expiresIn": 7200
      },
      "refreshToken": {
        "token": "eyJhbG...",
        "expiresIn": 604800
      }
    },
    "user": {
      "id": "1",
      "email": "user@example.com",
      "role": "user",
      "name": "普通用户"
    }
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

#### 错误响应
- 状态码：`401 Unauthorized`
```json
{
  "error": {
    "code": "AUTH_001",
    "message": "邮箱或密码不正确",
    "target": "credentials",
    "source": "auth.login"
  },
  "requestId": "req_123abc",
  "timestamp": 1647834567890
}
```

### 3.2 刷新令牌

#### 请求
- 方法：`POST`
- 路径：`/api/auth/refresh`
- 内容类型：`application/json`

```json
{
  "refreshToken": "eyJhbG..."
}
```

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "accessToken": {
      "token": "eyJhbG...",
      "expiresIn": 7200
    }
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

### 3.3 登出

#### 请求
- 方法：`POST`
- 路径：`/api/auth/logout`
- 需要认证：是

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "success": true
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

### 3.4 验证令牌

#### 请求
- 方法：`GET`
- 路径：`/api/auth/verify`
- 需要认证：是

#### 成功响应
- 状态码：`200 OK`
```json
{
  "data": {
    "authenticated": true,
    "user": {
      "id": "1",
      "email": "user@example.com",
      "role": "user",
      "name": "普通用户"
    }
  },
  "metadata": {
    "timestamp": 1647834567890,
    "requestId": "req_123abc"
  }
}
```

## 4. 错误代码

| 错误代码 | HTTP 状态码 | 描述 |
|----------|------------|------|
| AUTH_001 | 401 | 未认证 |
| AUTH_002 | 401 | 无效的令牌 |
| AUTH_003 | 401 | 令牌已过期 |
| AUTH_004 | 403 | 权限不足 |
| REQ_001 | 400 | 无效的请求格式 |
| REQ_002 | 400 | 缺少必要参数 |
| REQ_003 | 400 | 参数格式错误 |
| REQ_004 | 429 | 请求频率超限 |

## 5. 安全措施

### 5.1 令牌安全
- Access Token 有效期：2小时
- Refresh Token 有效期：7天
- 使用 HTTP-Only Cookie 存储 Refresh Token
- Access Token 仅存储在内存中

### 5.2 请求安全
- 所有请求必须使用 HTTPS
- 实现 CSRF 保护
- 请求参数验证和清理
- 适当的 CORS 策略

### 5.3 速率限制
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1616789000
```

## 6. 客户端集成

### 6.1 认证中间件配置
```typescript
const authConfig: AuthMiddlewareConfig = {
  requireAuth: true,
  allowedRoles: ['user', 'admin'],
  requireSession: false
};
```

### 6.2 错误处理
```typescript
try {
  const response = await api.post('/auth/login', credentials);
  // 处理成功响应
} catch (error) {
  if (error.code === 'AUTH_001') {
    // 处理未认证错误
  } else if (error.code === 'REQ_004') {
    // 处理请求频率限制
  }
}
```

---

最后更新: 2024-03-24
