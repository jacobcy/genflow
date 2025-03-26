import { useState, useEffect } from 'react';
import { Message } from '@/types/common';

export function useArticleChat(articleId: string) {
    // 从 localStorage 加载对话历史
    const loadChatHistory = (): Message[] => {
        try {
            const history = localStorage.getItem(`article_chat_${articleId}`);
            return history ? JSON.parse(history) : [];
        } catch (error) {
            console.error('Failed to load chat history:', error);
            return [];
        }
    };

    const [messages, setMessages] = useState<Message[]>(loadChatHistory);

    // 当消息更新时，保存到 localStorage
    useEffect(() => {
        try {
            localStorage.setItem(`article_chat_${articleId}`, JSON.stringify(messages));
        } catch (error) {
            console.error('Failed to save chat history:', error);
        }
    }, [messages, articleId]);

    // 添加新消息
    const addMessage = (content: string, role: 'user' | 'assistant' = 'user', type: 'text' | 'markdown' = 'text') => {
        const newMessage = {
            id: Date.now().toString(),
            content,
            role,
            type,
            timestamp: new Date().toISOString()
        } satisfies Message;
        setMessages(prev => [...prev, newMessage]);
        return newMessage;
    };

    // 清空对话历史
    const clearHistory = () => {
        setMessages([]);
        localStorage.removeItem(`article_chat_${articleId}`);
    };

    return {
        messages,
        addMessage,
        clearHistory,
        setMessages
    };
}
