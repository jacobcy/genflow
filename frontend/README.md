# GenFlow Frontend

GenFlow 是一个现代化的内容创作平台，集成了 AI 辅助写作、Markdown 编辑器和多平台发布功能。这个仓库包含了 GenFlow 的前端代码。

## 技术栈

- [Next.js 14](https://nextjs.org/) - React 框架
- [TypeScript](https://www.typescriptlang.org/) - 类型安全
- [TailwindCSS](https://tailwindcss.com/) - 样式系统
- [Framer Motion](https://www.framer.com/motion/) - 动画库

## 开发

首先，安装依赖：

```bash
pnpm install
```

然后，启动开发服务器：

```bash
pnpm dev
```

在浏览器中打开 [http://localhost:3000](http://localhost:3000) 查看结果。

## 构建

构建生产版本：

```bash
pnpm build
```

启动生产服务器：

```bash
pnpm start
```

## 代码质量

运行代码检查：

```bash
pnpm lint
```

修复代码问题：

```bash
pnpm lint:fix
```

## 目录结构

```
src/
  ├── app/              # App Router 路由和页面
  ├── components/       # React 组件
  │   ├── home/        # 主页相关组件
  │   └── layout/      # 布局组件
  ├── styles/          # 全局样式
  └── types/           # TypeScript 类型定义
```

## 贡献

1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的改动 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 许可证

[MIT](LICENSE)
