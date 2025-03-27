这里是针对GenFlow核心组件的测试规划：

## 测试架构规划

### 1. 核心服务测试分离

**test_topic_service.py**
- 专注测试话题获取、保存、状态更新等核心功能
- 重点：`get_topic`, `save_topic`, `select_topic_for_production`
- 避免：UI相关、复杂业务逻辑组合

**test_article_service.py**
- 专注文章生成、保存、获取等核心能力
- 重点：`create_article`, `save_article`, `get_article_by_topic`
- 避免：测试全流程生成逻辑

**test_config_service.py**
- 专注配置读取、更新、验证等功能
- 重点：`load_config`, `save_config`, `validate_config`
- 避免：测试具体配置项逻辑

**test_db_adapter.py**
- 专注数据访问层的基础操作
- 重点：`initialize`, `get_topic`, `save_article`等原子操作
- 避免：测试与数据库实现相关的细节

### 2. 核心流程测试

**test_process.py**
- 专注内容生成流程的关键节点测试
- 重点：`process_topic`, `generate_content`等流程函数
- 避免：完整端到端测试，专注于关键流程节点

### 3. 内容管理测试

**test_content_manager.py**
- 专注ContentManager独立实现的方法
- 重点：内容管理核心API（不与其他测试重复）
- 避免：重复测试底层服务已测试的功能

### 测试策略关键点

1. **专注核心路径**：每个测试文件只测试关键功能点
2. **避免重复测试**：各组件测试不重复测试相同功能
3. **模块化Mock**：统一Mock对象的创建方式
4. **轻量级测试**：不依赖真实数据库/外部系统
5. **清晰断言**：每个测试只验证一个关键结果

这种架构将确保覆盖所有核心功能，同时避免测试重复和维护困难。每个测试文件都有明确的责任边界，使测试更易于维护和理解。
