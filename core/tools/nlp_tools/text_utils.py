"""文本处理工具

提供文本分析和处理的常用功能。
"""
import re
from typing import Optional, Dict, List, Union

def count_words(text: Union[str, Dict, List], chinese_as_word: bool = True) -> int:
    """统计文本中的字数

    对于中文文本，默认每个汉字算作一个词。
    对于英文文本，按空格分词计数。
    对于字典或列表，会递归统计所有文本。

    Args:
        text: 要统计的文本、字典或列表
        chinese_as_word: 是否将每个汉字视为一个词，默认为True

    Returns:
        int: 字数统计
    """
    if not text:
        return 0

    # 处理字典
    if isinstance(text, dict):
        count = 0
        for value in text.values():
            count += count_words(value, chinese_as_word)
        return count

    # 处理列表
    if isinstance(text, list):
        count = 0
        for item in text:
            count += count_words(item, chinese_as_word)
        return count

    # 确保是字符串
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return 0

    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # 移除多余空白
    text = re.sub(r'\s+', ' ', text).strip()

    if not text:
        return 0

    if chinese_as_word:
        # 中文每个字符算一个词
        # 匹配CJK字符（中日韩文字）
        chinese_chars = re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u2a700-\u2b73f\u2b740-\u2b81f\u2b820-\u2ceaf\uf900-\ufaff\u3300-\u33ff\ufe30-\ufe4f\uf900-\ufaff\ufe30-\ufe4f\u2f800-\u2fa1f]', text)

        # 匹配非CJK单词
        non_chinese_words = re.findall(r'[a-zA-Z0-9_\-\']+', text)

        return len(chinese_chars) + len(non_chinese_words)
    else:
        # 按空格分词统计
        return len(text.split())
