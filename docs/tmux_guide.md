# Tmux 使用指南

## 目录
- [简介](#简介)
- [基本概念](#基本概念)
- [安装](#安装)
- [基础命令](#基础命令)
- [会话管理](#会话管理)
- [窗口管理](#窗口管理)
- [面板管理](#面板管理)
- [复制模式](#复制模式)
- [常用配置](#常用配置)
- [最佳实践](#最佳实践)

## 简介

Tmux 是一个终端复用器（terminal multiplexer），它允许在单个终端窗口中运行多个终端会话。使用 tmux 可以：

- 在单个窗口中同时运行多个程序
- 断开并重新连接到运行中的会话
- 在远程服务器上保持会话运行
- 共享会话与他人协作

## 基本概念

Tmux 有三个重要的基本概念：

1. **会话（Session）**：一个独立的工作区，包含一个或多个窗口
2. **窗口（Window）**：相当于标签页，每个窗口占满整个屏幕
3. **面板（Pane）**：窗口内的分屏，可以在一个窗口中显示多个终端

## 安装

### macOS
```bash
brew install tmux
```

### Ubuntu/Debian
```bash
sudo apt-get install tmux
```

### CentOS/RHEL
```bash
sudo yum install tmux
```

## 基础命令

### 启动与退出
```bash
# 启动新会话
tmux

# 启动新会话并命名
tmux new -s session_name

# 退出当前会话
exit
# 或按 Ctrl+B 后输入 :kill-session

# 关闭服务器（关闭所有会话）
tmux kill-server
```

## 会话管理

所有命令前缀：`Ctrl+B`（下面用 `<prefix>` 表示）

### 基本操作
```bash
# 创建新会话
tmux new -s session_name

# 列出所有会话
tmux ls

# 连接到指定会话
tmux attach -t session_name

# 断开当前会话
<prefix> d

# 重命名当前会话
<prefix> $

# 切换会话
<prefix> s  # 显示会话列表并选择
<prefix> (  # 切换到上一个会话
<prefix> )  # 切换到下一个会话

# 关闭会话
tmux kill-session -t session_name
```

## 窗口管理

### 基本操作
```bash
# 创建新窗口
<prefix> c

# 切换窗口
<prefix> 0-9  # 切换到指定编号的窗口
<prefix> n    # 切换到下一个窗口
<prefix> p    # 切换到上一个窗口
<prefix> w    # 显示窗口列表

# 重命名窗口
<prefix> ,

# 关闭窗口
<prefix> &
```

## 面板管理

### 分割面板
```bash
# 垂直分割
<prefix> %

# 水平分割
<prefix> "
```

### 面板操作
```bash
# 切换面板
<prefix> 方向键  # 使用方向键切换到相邻面板
<prefix> o      # 切换到下一个面板
<prefix> ;      # 切换到上一个面板

# 调整面板大小
<prefix> Alt+方向键  # 以 1 个单位调整
<prefix> Ctrl+方向键 # 以 5 个单位调整

# 关闭面板
<prefix> x

# 最大化/还原面板
<prefix> z
```

## 复制模式

### 进入复制模式
```bash
<prefix> [  # 进入复制模式
q          # 退出复制模式
```

### 在复制模式中
```bash
# 移动
h, j, k, l  # vim 风格移动
方向键      # 移动光标
w, b        # 向前/后移动一个词
g, G        # 移动到开头/结尾

# 复制
空格键      # 开始选择
Enter       # 复制选中内容并退出复制模式
```

### 粘贴
```bash
<prefix> ]  # 粘贴最近一次复制的内容
```

## 常用配置

创建 `~/.tmux.conf` 文件，添加以下配置：

```bash
# 修改前缀键为 Ctrl+A
set -g prefix C-a
unbind C-b
bind C-a send-prefix

# 启用鼠标
set -g mouse on

# 设置窗口和面板的索引从 1 开始
set -g base-index 1
setw -g pane-base-index 1

# 设置状态栏
set -g status-bg black
set -g status-fg white
```

## 最佳实践

1. **会话命名规范**
   - 使用有意义的会话名称
   - 建议按项目或功能命名
   - 例如：`tmux new -s project_dev`

2. **窗口组织**
   - 一个会话用于一个项目
   - 不同功能使用不同窗口
   - 合理使用窗口命名

3. **快捷键使用**
   - 熟记常用快捷键
   - 使用配置文件自定义快捷键
   - 建议将前缀键改为更方便的组合

4. **远程使用**
   - 在远程服务器上使用 tmux 保持会话
   - 断开连接后可重新连接
   - 避免网络中断影响工作

5. **协作方式**
   - 多人可以连接到同一个会话
   - 适合结对编程和远程协助
   - 注意权限管理

## 常见问题解决

1. **会话假死**
   ```bash
   # 强制关闭会话
   tmux kill-session -t session_name
   ```

2. **清理所有会话**
   ```bash
   # 关闭所有会话
   tmux kill-server
   ```

3. **查找特定会话**
   ```bash
   # 使用 grep 过滤会话
   tmux ls | grep "session_name"
   ```

4. **恢复断开的会话**
   ```bash
   # 列出会话并重新连接
   tmux ls
   tmux attach -t session_name
   ```

## 进阶技巧

1. **会话嵌套**
   - 在 tmux 中使用 tmux 时注意前缀键冲突
   - 可以使用不同的前缀键区分

2. **脚本自动化**
   - 使用脚本自动创建会话和窗口布局
   - 自动化开发环境配置

3. **状态栏定制**
   - 显示系统信息
   - 显示项目相关信息
   - 自定义样式和颜色

4. **插件管理**
   - 使用 TPM (Tmux Plugin Manager)
   - 安装常用插件
   - 管理配置
