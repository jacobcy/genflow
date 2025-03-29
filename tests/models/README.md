# GenFlow 模型层测试指南

本文档提供了对 GenFlow 模型层测试的指导原则和使用说明。

## 测试原则

根据 GenFlow 核心模型开发指南，我们遵循以下测试原则：

### 1. 最小可行测试

- 测试只关注核心功能，确保模型层的基本功能可用
- 不进行深入的边界测试或性能测试
- 优先测试常规路径，而非异常路径

### 2. 测试内容

测试覆盖以下核心功能：

- 配置管理（内容类型、文章风格、平台）
- 数据操作（话题、大纲、文章）
- 配置同步（导入/导出配置）
- 基本错误处理

### 3. 测试类型

- **单元测试**：测试各模块的独立功能
- **简化集成测试**：测试主要组件间的交互
- **功能测试**：验证通过 ContentManager 暴露的 API 是否能正常工作

## 核心测试文件

GenFlow 模型层的关键测试文件：

1. **test_models_basic.py** - 基础功能测试，一站式验证核心功能
2. **test_topic_simplified.py** - 简化版话题模型测试
3. **test_manager_integration.py** - 管理器集成测试
4. **test_article_standalone.py** - 文章模块独立测试
5. **test_db_adapter.py** - 数据库适配器测试
6. **test_content_manager.py** - ContentManager功能测试

## 冗余测试文件

以下文件仅作为参考，不是运行测试所必需的：

- **test_style_simplified.py** - 风格管理的简化测试
- **test_research_simplified.py** - 研究模块的简化测试

## 运行测试

### 基本测试

运行基础功能测试（推荐）：

```bash
pytest tests/models/test_models_basic.py -v
```

### 集成测试

运行管理器集成测试：

```bash
pytest tests/models/test_manager_integration.py -v
```

### 全部测试

运行全部核心测试：

```bash
pytest tests/models/test_models_basic.py tests/models/test_manager_integration.py -v
```

## 测试数据说明

测试使用以下类型的测试数据：

1. **模拟数据** - 为测试目的创建的临时数据
2. **临时配置文件** - 测试运行时创建，测试结束后自动清理
3. **临时数据库** - 测试过程中使用临时SQLite数据库

## 注意事项

1. 所有测试都使用隔离的环境，不会影响生产数据库
2. 测试自动创建临时目录和数据库，测试结束后自动清理
3. 测试不依赖外部服务，可以在任何环境中运行
4. 测试主要验证API接口的正确性，不深入测试内部实现

## 贡献新测试

添加新测试时，请遵循以下规则：

1. 专注于核心功能，避免复杂边界测试
2. 使用明确的测试名称描述测试内容
3. 使用隔离环境确保测试的可重复性
4. 遵循"一个测试一个责任"的原则

按照这些原则，我们可以确保模型层测试简洁有效，加速开发进程，同时保证系统的基本功能可用。
