"""话题知识图谱工具

实验性功能：构建热点话题的知识图谱。
使用外部 API (如 Dify) 进行实体识别和关系抽取。
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class Entity(BaseModel):
    """实体模型"""
    id: str
    name: str
    type: str
    source: str = Field(description="实体来源（话题标题/描述）")
    timestamp: int = Field(description="首次发现时间")

class Relation(BaseModel):
    """关系模型"""
    source_id: str
    target_id: str
    type: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: int

class TopicKnowledgeGraph:
    """话题知识图谱

    实验性质的知识图谱构建工具，用于：
    1. 从热点话题中识别实体
    2. 分析实体间关系
    3. 构建简单的知识网络
    4. 追踪热点话题演变

    注意：这是一个实验性功能，主要用于研究和测试。
    生产环境建议使用专门的图数据库和知识图谱服务。
    """

    def __init__(self, api_endpoint: str, api_key: str):
        """初始化知识图谱工具

        Args:
            api_endpoint: 外部API地址（如Dify API）
            api_key: API密钥
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []

    async def extract_entities(self, topic: Dict) -> List[Entity]:
        """从话题中提取实体

        Args:
            topic: 话题数据

        Returns:
            List[Entity]: 识别出的实体列表
        """
        # 构建提示词
        title = topic.get("title", "")
        desc = topic.get("description", "")
        prompt = f"""请从以下文本中识别重要实体（人物、组织、地点、事件等），格式要求：
        - 每行一个实体
        - 实体类型用[]标注
        - 示例：张三[人物]

        文本内容：
        标题：{title}
        描述：{desc}
        """

        try:
            # 调用外部API进行实体识别
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_endpoint}/completion",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "prompt": prompt,
                        "temperature": 0.1
                    }
                )

                if response.status_code != 200:
                    logger.error(f"API调用失败: {response.status_code}")
                    return []

                # 解析返回的实体
                entities = []
                for line in response.json()["text"].split("\n"):
                    if not line.strip():
                        continue
                    try:
                        name, type_str = line.split("[")
                        entity_type = type_str.rstrip("]")
                        entity = Entity(
                            id=f"{name}_{len(self.entities)}",
                            name=name.strip(),
                            type=entity_type,
                            source="title" if name in title else "description",
                            timestamp=topic.get("timestamp", int(datetime.now().timestamp()))
                        )
                        entities.append(entity)
                    except Exception as e:
                        logger.warning(f"实体解析失败: {e}, 原文: {line}")
                        continue

                return entities

        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            return []

    async def analyze_relations(self, entities: List[Entity]) -> List[Relation]:
        """分析实体间的关系

        Args:
            entities: 实体列表

        Returns:
            List[Relation]: 识别出的关系列表
        """
        if len(entities) < 2:
            return []

        # 构建提示词
        entities_text = "\n".join([f"{e.name}[{e.type}]" for e in entities])
        prompt = f"""请分析以下实体之间可能存在的关系，格式要求：
        - 每行一个关系
        - 格式：实体1|关系类型|实体2|可信度
        - 可信度范围：0.0-1.0
        - 示例：张三|隶属于|某公司|0.9

        实体列表：
        {entities_text}
        """

        try:
            # 调用外部API分析关系
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_endpoint}/completion",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "prompt": prompt,
                        "temperature": 0.2
                    }
                )

                if response.status_code != 200:
                    logger.error(f"API调用失败: {response.status_code}")
                    return []

                # 解析返回的关系
                relations = []
                entity_map = {e.name: e.id for e in entities}

                for line in response.json()["text"].split("\n"):
                    if not line.strip():
                        continue
                    try:
                        source, rel_type, target, conf = line.split("|")
                        if source.strip() in entity_map and target.strip() in entity_map:
                            relation = Relation(
                                source_id=entity_map[source.strip()],
                                target_id=entity_map[target.strip()],
                                type=rel_type.strip(),
                                confidence=float(conf),
                                timestamp=int(datetime.now().timestamp())
                            )
                            relations.append(relation)
                    except Exception as e:
                        logger.warning(f"关系解析失败: {e}, 原文: {line}")
                        continue

                return relations

        except Exception as e:
            logger.error(f"关系分析失败: {e}")
            return []

    async def process_topic(self, topic: Dict) -> Tuple[List[Entity], List[Relation]]:
        """处理单个话题，提取实体和关系

        Args:
            topic: 话题数据

        Returns:
            Tuple[List[Entity], List[Relation]]: 识别出的实体和关系
        """
        # 提取实体
        entities = await self.extract_entities(topic)
        if not entities:
            return [], []

        # 分析关系
        relations = await self.analyze_relations(entities)

        # 更新知识图谱
        for entity in entities:
            self.entities[entity.id] = entity
        self.relations.extend(relations)

        return entities, relations

    def get_graph_data(self) -> Dict:
        """获取知识图谱数据

        Returns:
            Dict: 知识图谱数据，包含实体和关系
        """
        return {
            "entities": [e.dict() for e in self.entities.values()],
            "relations": [r.dict() for r in self.relations]
        }

    def clear(self):
        """清空知识图谱数据"""
        self.entities.clear()
        self.relations.clear()
