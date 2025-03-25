# GenFlow API 统一规范

## 1. 认证机制

### 1.1 Token 结构
```typescript
interface JWTPayload {
  userId: string;
  role: 'user' | 'admin';
  sessionId?: string;  // AI会话ID，用于写作助手
  exp: number;        // 过期时间
  iat: number;        // 签发时间
}
```

### 1.2 认证头格式
```http
Authorization: Bearer <token>
```

### 1.3 Token 管理
```typescript
interface TokenPair {
  accessToken: {
    token: string;
    expiresIn: number;  // 2小时
  };
  refreshToken: {
    token: string;
    expiresIn: number;  // 7天
  };
}
```

### 1.4 认证中间件
```typescript
interface AuthMiddlewareConfig {
  requireAuth: boolean;      // 是否需要认证
  allowedRoles?: string[];   // 允许的角色
  requireSession?: boolean;  // 是否需要AI会话
}
```

## 2. 错误处理

### 2.1 统一错误响应
```typescript
interface APIError {
  error: {
    code: ErrorCode;
    message: string;
    details?: any;
    target?: string;    // 错误发生的位置
    source?: string;    // 错误来源
  };
  requestId: string;    // 用于追踪
  timestamp: number;    // 错误发生时间
}
```

### 2.2 标准错误代码
```typescript
enum ErrorCode {
  // 认证相关 (1xxx)
  UNAUTHORIZED = 'AUTH_001',
  INVALID_TOKEN = 'AUTH_002',
  TOKEN_EXPIRED = 'AUTH_003',
  INSUFFICIENT_PERMISSIONS = 'AUTH_004',
  SESSION_EXPIRED = 'AUTH_005',

  // 请求相关 (2xxx)
  INVALID_REQUEST = 'REQ_001',
  MISSING_PARAMETER = 'REQ_002',
  INVALID_PARAMETER = 'REQ_003',
  RATE_LIMIT_EXCEEDED = 'REQ_004',

  // 资源相关 (3xxx)
  RESOURCE_NOT_FOUND = 'RES_001',
  RESOURCE_CONFLICT = 'RES_002',
  RESOURCE_FORBIDDEN = 'RES_003',

  // AI服务相关 (4xxx)
  AI_SERVICE_ERROR = 'AI_001',
  AI_TIMEOUT = 'AI_002',
  AI_INVALID_RESPONSE = 'AI_003',
  AI_CONTENT_FILTER = 'AI_004',

  // 写作工具相关 (5xxx)
  EDITOR_SYNC_ERROR = 'EDIT_001',
  VERSION_CONFLICT = 'EDIT_002',
  INVALID_OPERATION = 'EDIT_003',

  // 系统错误 (9xxx)
  INTERNAL_ERROR = 'SYS_001',
  SERVICE_UNAVAILABLE = 'SYS_002',
  DATABASE_ERROR = 'SYS_003'
}
```

### 2.3 HTTP状态码映射
```typescript
const ErrorHttpStatusMap = {
  // 认证相关
  'AUTH_001': 401,  // Unauthorized
  'AUTH_002': 401,
  'AUTH_003': 401,
  'AUTH_004': 403,  // Forbidden
  'AUTH_005': 401,

  // 请求相关
  'REQ_001': 400,  // Bad Request
  'REQ_002': 400,
  'REQ_003': 400,
  'REQ_004': 429,  // Too Many Requests

  // 资源相关
  'RES_001': 404,  // Not Found
  'RES_002': 409,  // Conflict
  'RES_003': 403,

  // AI服务相关
  'AI_001': 502,   // Bad Gateway
  'AI_002': 504,   // Gateway Timeout
  'AI_003': 502,
  'AI_004': 422,   // Unprocessable Entity

  // 写作工具相关
  'EDIT_001': 409,
  'EDIT_002': 409,
  'EDIT_003': 400,

  // 系统错误
  'SYS_001': 500,  // Internal Server Error
  'SYS_002': 503,  // Service Unavailable
  'SYS_003': 500
};
```

## 3. 响应封装

### 3.1 成功响应
```typescript
interface APIResponse<T> {
  data: T;
  metadata?: {
    timestamp: number;
    requestId: string;
    page?: number;
    pageSize?: number;
    total?: number;
  };
}
```

### 3.2 分页响应
```typescript
interface PaginatedResponse<T> extends APIResponse<T[]> {
  metadata: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}
```

## 4. 请求验证

### 4.1 请求头验证
```typescript
interface RequiredHeaders {
  'Authorization': string;
  'Content-Type': string;
  'Accept': string;
  'X-Request-ID'?: string;
  'X-Client-Version'?: string;
}
```

### 4.2 参数验证规则
```typescript
interface ValidationRules {
  required?: boolean;
  type?: string;
  min?: number;
  max?: number;
  pattern?: RegExp;
  custom?: (value: any) => boolean;
}
```

## 5. 速率限制

### 5.1 限制规则
```typescript
interface RateLimitConfig {
  path: string;
  limit: number;
  window: number;  // 时间窗口（秒）
  scope: 'user' | 'ip' | 'global';
}
```

### 5.2 响应头
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1616789000
```

## 6. 安全措施

### 6.1 Token 安全
- 使用 HTTP Only Cookies 存储 refresh token
- Access token 仅存储在内存中
- 定期轮换密钥
- Token 撤销机制

### 6.2 请求安全
- 所有请求使用 HTTPS
- 实现 CSRF 保护
- 设置适当的 CORS 策略
- 请求参数验证和清理

### 6.3 数据安全
- 敏感数据加密存储
- 日志脱敏
- 定期数据备份
- 访问审计日志

## 7. 实现示例

### 7.1 错误处理中间件
```typescript
async function errorHandler(err: any, req: Request, res: Response, next: NextFunction) {
  const error: APIError = {
    error: {
      code: err.code || 'SYS_001',
      message: err.message || '系统内部错误',
      details: err.details,
      target: err.target,
      source: err.source
    },
    requestId: req.headers['x-request-id'] || uuid(),
    timestamp: Date.now()
  };

  const status = ErrorHttpStatusMap[error.error.code] || 500;
  res.status(status).json(error);
}
```

### 7.2 认证中间件
```typescript
async function authMiddleware(config: AuthMiddlewareConfig) {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      const token = req.headers.authorization?.split(' ')[1];
      if (!token && config.requireAuth) {
        throw new APIError('AUTH_001', '未认证');
      }

      const payload = jwt.verify(token, process.env.JWT_SECRET);
      if (config.allowedRoles && !config.allowedRoles.includes(payload.role)) {
        throw new APIError('AUTH_004', '权限不足');
      }

      if (config.requireSession && !payload.sessionId) {
        throw new APIError('AUTH_005', '无效的会话');
      }

      req.user = payload;
      next();
    } catch (err) {
      next(err);
    }
  };
}
```

## 8. 使用指南

### 8.1 API实现清单
- [ ] 实现统一错误处理中间件
- [ ] 实现认证中间件
- [ ] 设置请求验证
- [ ] 配置速率限制
- [ ] 实现安全措施
- [ ] 添加日志记录
- [ ] 设置监控指标

### 8.2 客户端集成
- [ ] 实现token管理
- [ ] 添加请求拦截器
- [ ] 实现错误处理
- [ ] 添加重试机制
- [ ] 实现请求队列
