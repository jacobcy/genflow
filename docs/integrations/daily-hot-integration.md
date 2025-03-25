# GenFlow DailyHot 集成指南

## 简介

GenFlow 集成了 [jacobcy/DailyHot](https://github.com/jacobcy/DailyHot) 和 [jacobcy/DailyHotApi](https://github.com/jacobcy/DailyHotApi) 作为热点聚合服务。这是一个强大的热点聚合系统，包含前端展示和后端 API 服务，支持多个热门平台的数据聚合。两个仓库均作为 Git 子模块集成在 `integrations` 目录下。

## 特性

### API 服务 (DailyHotApi)
- 🔥 支持微博、知乎、36氪等多个热门平台
- 📊 统一的数据格式和 API 接口
- 🚀 支持 RSS 订阅模式
- ⚡️ 数据自动更新和缓存机制
- 🌐 支持 Vercel 一键部署

### 前端界面 (DailyHot)
- 🎨 美观的用户界面
- 📱 响应式设计，支持移动端
- 🌈 支持多种主题切换
- 🔄 实时数据更新
- 💾 本地收藏功能

## 子模块管理

### 1. 初始化子模块

对于新克隆的项目：

```bash
# 克隆项目时包含子模块
git clone --recursive https://github.com/your-username/genflow.git

# 或者在已克隆的项目中初始化子模块
git submodule update --init --recursive
```

### 2. 更新子模块

```bash
# 更新所有子模块到最新版本
git submodule update --remote

# 更新特定子模块
git submodule update --remote integrations/daily-hot
git submodule update --remote integrations/daily-hot-api

# 提交子模块更新
git add integrations/daily-hot integrations/daily-hot-api
git commit -m "chore: update daily-hot submodules"
```

## 开发环境配置

### 1. API 服务配置

#### 环境要求
- Node.js >= 16.0.0
- npm 或 pnpm

#### 安装和启动

```bash
# 进入 API 目录
cd integrations/daily-hot-api

# 安装依赖
pnpm install

# 开发模式启动
pnpm dev

# 生产模式构建
pnpm build
pnpm start
```

### 2. 前端配置

#### 环境要求
- Node.js >= 16.0.0
- npm 或 pnpm
- Vite

#### 安装和启动

```bash
# 进入前端目录
cd integrations/daily-hot

# 安装依赖
pnpm install

# 开发模式启动
pnpm dev

# 生产模式构建
pnpm build
```

## 部署说明

### 1. API 服务部署

支持多种部署方式：

#### Docker 部署

```bash
# 构建镜像
docker build -t daily-hot-api .

# 运行容器
docker run --restart always -p 6688:6688 -d daily-hot-api

# 或使用 Docker Compose
docker-compose up -d
```

#### Vercel 部署

1. Fork DailyHotApi 仓库
2. 在 Vercel 中导入项目
3. 配置环境变量（如需要）
4. 点击部署

#### 传统部署

```bash
# 安装 pm2
npm i pm2 -g

# 使用 pm2 部署
sh ./deploy.sh
```

### 2. 前端部署

#### Vercel 部署

1. Fork DailyHot 仓库
2. 在 Vercel 中导入项目
3. 配置 API 地址
4. 点击部署

#### 静态部署

```bash
# 构建
pnpm build

# 将 dist 目录部署到任意静态服务器
```

## 配置说明

### 1. API 服务配置

在 `.env` 文件中配置：

```env
# 服务端口
PORT=6688

# 缓存时间（分钟）
CACHE_TIME=60

# 代理配置（可选）
PROXY_HOST=
PROXY_PORT=
```

### 2. 前端配置

在 `.env` 文件中配置：

```env
# API 地址
VITE_API_URL=http://localhost:6688

# 主题配置
VITE_THEME=light
```

## 数据源支持

当前支持的数据源包括：

| 平台 | 类型 | 接口路径 |
|------|------|----------|
| 微博 | 热搜 | /weibo |
| 知乎 | 热榜 | /zhihu |
| 36氪 | 热榜 | /36kr |
| 百度 | 热搜 | /baidu |
| 抖音 | 热点 | /douyin |
| 微信 | 热文 | /weixin |
| B站 | 热榜 | /bilibili |
| 少数派 | 热榜 | /sspai |
| IT之家 | 热榜 | /ithome |
| V2EX | 最热 | /v2ex |

## 最佳实践

1. **缓存策略**
   - 合理配置缓存时间
   - 使用 CDN 加速静态资源
   - 实现数据预加载

2. **性能优化**
   - 启用 Gzip 压缩
   - 实现懒加载和分页
   - 优化图片加载

3. **错误处理**
   - 实现优雅的降级策略
   - 添加错误重试机制
   - 完善的错误提示

## 常见问题

1. **API 访问失败**
   - 检查网络连接
   - 验证 API 地址配置
   - 查看服务器日志

2. **数据更新延迟**
   - 检查缓存配置
   - 验证定时任务状态
   - 确认数据源可用性

3. **部署问题**
   - 确认环境变量配置
   - 检查端口占用情况
   - 验证构建输出

## 贡献指南

1. API 相关改进请在 [jacobcy/DailyHotApi](https://github.com/jacobcy/DailyHotApi) 提交 PR
2. 前端相关改进请在 [jacobcy/DailyHot](https://github.com/jacobcy/DailyHot) 提交 PR
3. 集成相关问题请在 GenFlow 主仓库提交 issue

## 许可证

- DailyHot: MIT License
- DailyHotApi: MIT License