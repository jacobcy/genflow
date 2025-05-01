"""Topic Factory

Handles business logic related to Topic creation, validation, and operations.
"""

from typing import List, Optional
from loguru import logger

from .topic import Topic
from .topic_manager import TopicManager

class TopicFactory:
    """Topic Factory class

    Responsible for topic-related business logic.
    Uses TopicManager for data persistence.
    """

    @classmethod
    def get_topic(cls, topic_id: str) -> Optional[Topic]:
        """Get a topic by its ID.

        Args:
            topic_id: The ID of the topic.

        Returns:
            The Topic object or None if not found.
        """
        logger.debug(f"Factory: Getting topic {topic_id}")
        # Future business logic/validation can go here
        topic = TopicManager.get_topic(topic_id)
        # Future transformation/enrichment can go here
        return topic

    @classmethod
    def save_topic(cls, topic: Topic) -> bool:
        """Save a topic.

        Args:
            topic: The Topic object to save.

        Returns:
            True if saving was successful, False otherwise.
        """
        # Future business logic/validation before saving
        if not isinstance(topic, Topic):
            logger.error("Invalid type provided to save_topic. Expected Topic.")
            return False

        logger.debug(f"Factory: Saving topic {topic.id}")
        # Update timestamps or other fields if needed at Factory level
        topic.update_timestamp() # Keep timestamp update logic here for now
        return TopicManager.save_topic(topic)

    @classmethod
    def delete_topic(cls, topic_id: str) -> bool:
        """Delete a topic by its ID.

        Args:
            topic_id: The ID of the topic to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        logger.debug(f"Factory: Deleting topic {topic_id}")
        # Future business logic/checks before deletion
        return TopicManager.delete_topic(topic_id)

    @classmethod
    def get_topics_by_platform(cls, platform: str) -> List[Topic]:
        """Get all topics for a specific platform.

        Args:
            platform: The platform identifier.

        Returns:
            A list of Topic objects.
        """
        logger.debug(f"Factory: Getting topics for platform {platform}")
        # Future filtering/sorting logic can go here
        topics = TopicManager.get_topics_by_platform(platform)
        # Future transformation can go here
        return topics

    # Add other topic-specific business logic methods here as needed
    # For example, methods to create topics from different sources,
    # methods to validate topic data, etc.