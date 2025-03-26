# GenFlow Markdown 编辑器集成指南

## 简介

GenFlow 集成了 [jacobcy/md](https://github.com/jacobcy/md) 作为其 Markdown 编辑器组件。这是一个基于 Vue3 的强大编辑器，专注于微信公众号排版，支持丰富的主题定制和图床配置。编辑器作为 Git 子模块集成在 `integrations` 目录下。

## 特性

- 🎨 支持 Markdown 所有基础语法和数学公式
- 📊 支持 Mermaid 图表渲染和 GFM 警告块
- 🌈 丰富的代码块高亮主题
- 🎯 自定义主题色和 CSS 样式
- 📤 多图上传功能，支持多种图床
- 💾 便捷的文件导入导出
- 📝 本地内容管理，自动保存草稿

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
git submodule update --remote integrations/md

# 提交子模块更新
git add integrations/md
git commit -m "chore: update md editor submodule"
```

### 3. 切换子模块版本

```bash
cd integrations/md
git checkout <tag/commit>  # 例如: git checkout v1.0.0
cd ../..
git add integrations/md
git commit -m "chore: update md editor to v1.0.0"
```

### 4. 删除子模块

如果需要删除子模块，请按以下步骤操作：

```bash
# 1. 取消注册子模块
git submodule deinit -f integrations/md

# 2. 删除子模块目录
rm -rf .git/modules/integrations/md

# 3. 删除子模块文件
git rm -f integrations/md

# 4. 提交更改
git commit -m "chore: remove md editor submodule"
```

## 开发环境配置

### 1. 环境要求

- Node.js >= 20.0.0
- npm 或 pnpm

### 2. 安装依赖

```bash
cd integrations/md
npm install  # 或者使用 pnpm install
```

### 3. 开发模式

```bash
# 启动开发服务器（默认端口 9000）
npm start
```

### 4. 构建部署

```bash
# 构建并部署在 /md 目录
npm run build
# 访问 http://localhost:9000/md

# 构建并部署在根目录
npm run build:h5-netlify
# 访问 http://localhost:9000/
```

## 配置说明

### 1. 部署说明

编辑器支持两种部署方式：

1. 子目录部署（默认）：
   - 构建命令：`npm run build`
   - 访问地址：`http://localhost:9000/md`
   - 适用场景：作为现有系统的一个子模块集成

2. 根目录部署：
   - 构建命令：`npm run build:h5-netlify`
   - 访问地址：`http://localhost:9000/`
   - 适用场景：独立部署或作为主应用

编辑器构建后的文件是纯静态的，可以通过任何 Web 服务器（如 Nginx、Apache）进行托管。

### 2. 图床配置

编辑器支持多种图床服务：

- GitHub
- 阿里云 OSS
- 腾讯云 COS
- 七牛云 Kodo
- MinIO
- 微信公众号
- Cloudflare R2
- 自定义上传

每种图床的具体配置参数请参考编辑器的设置面板。

### 3. 主题定制

可以通过编辑器设置面板自定义：

- 主题色
- 代码高亮主题
- 自定义 CSS 样式

## 最佳实践

1. **子模块管理**
   - 始终使用特定的版本标签或提交 SHA
   - 在更新前测试新版本的兼容性
   - 保持团队成员的子模块同步

2. **开发流程**
   - 使用开发模式进行本地调试
   - 定期同步上游更新
   - 记录重要的配置变更

3. **部署注意事项**
   - 确保构建输出目录正确配置
   - 检查图床配置的正确性
   - 验证自定义样式的兼容性

## 常见问题

1. **子模块更新失败**
   - 检查 Git 配置是否正确
   - 确保有正确的访问权限
   - 尝试清理并重新初始化子模块

2. **编辑器启动问题**
   - 确认 Node.js 版本 >= 20
   - 检查依赖是否完整安装
   - 查看开发服务器日志

3. **图片上传失败**
   - 验证图床配置参数
   - 检查网络连接
   - 查看浏览器控制台错误信息

## 贡献指南

1. 对于编辑器核心功能的改进，请在 [jacobcy/md](https://github.com/jacobcy/md) 提交 PR
2. 对于集成相关的问题，请在 GenFlow 主仓库提交 issue

## 许可证

编辑器使用 WTFPL 许可证
