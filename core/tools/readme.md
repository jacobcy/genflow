# GenFlow 工具集

GenFlow 提供了一系列强大的工具，用于内容收集、NLP处理、搜索和风格适配等任务。所有工具都实现了缓存机制，避免重复初始化，提高性能。

## 内容收集工具 (content_collectors)

用于从各种来源收集和解析内容的工具集。

### ContentCollector

统一的内容收集器，支持多源采集：

```python
collector = ContentCollector.get_instance()

# 搜索内容
results = await collector.search_all("关键词")

# 解析单个URL
content = await collector.get_content("https://example.com")

# 批量解析URL
contents = await collector.batch_collect(["url1", "url2"])
```

支持的解析器：
- `NewspaperParser`: 使用 newspaper3k 解析新闻文章
- `TrafilaturaParser`: 使用 Trafilatura 解析通用网页
- `FirecrawlParser`: 使用 Firecrawl API 解析复杂网页

支持的内容源：
- `GoogleTrendsSource`: 获取 Google Trends 相关内容
- `FirecrawlSource`: 使用 Firecrawl 搜索内容

## NLP 工具 (nlp_tools)

自然语言处理工具集，提供文本分析能力。

```python
nlp = NLPAggregator.get_instance()

# 执行 NLP 任务
result = await nlp.execute(text)
```

## 搜索工具 (search_tools)

提供多源搜索能力的工具集。

```python
search = SearchEngine.get_instance()

# 执行搜索
results = await search.search(query)
```

## 风格工具 (style_tools)

用于内容风格适配的工具集。

```python
adapter = StyleAdapter.get_instance(platform)

# 适配内容风格
styled_content = await adapter.adapt(content)
```

## 工具特性

所有工具都具有以下特性：

1. **单例模式**：使用 `get_instance()` 获取工具实例，避免重复初始化
2. **健康检查**：支持 `health_check()` 方法检查工具状态
3. **缓存管理**：提供 `clear_cache()` 方法清理缓存
4. **异步支持**：所有操作都支持异步调用
5. **错误处理**：统一的错误处理和日志记录
6. **可扩展性**：支持注册新的解析器和内容源

## 配置要求

某些工具需要配置特定的 API 密钥：

- `FIRECRAWL_API_KEY`: Firecrawl API 访问密钥
- `SERP_API_KEY`: SERP API 访问密钥
- `LANGUAGE`: 默认语言设置 (如 'zh' 为中文)

## 使用建议

1. 优先使用工具的 `get_instance()` 方法获取实例
2. 在批量处理时使用 `batch_collect()` 等批处理方法
3. 定期执行 `health_check()` 确保工具正常运行
4. 在需要时使用 `clear_cache()` 清理缓存
5. 使用异步方法提高性能
