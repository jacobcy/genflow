import React, { useState, useCallback } from 'react';
import { ActionButton } from '@/types/ai-assistant';
import { Message } from '@/types/common';
import ChatInterface from './ChatInterface';
import ActionButtons from './ActionButtons';
import { useArticleChat } from '@/hooks/useArticleChat';

interface AIAssistantProps {
    userId: string;
    articleId: string;
    className?: string;
}

export default function AIAssistant({ userId, articleId, className }: AIAssistantProps) {
    const { messages, addMessage, setMessages, clearHistory } = useArticleChat(articleId);
    const [actions, setActions] = useState<ActionButton[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleClearChat = useCallback(() => {
        clearHistory();
        setActions([]);
    }, [clearHistory]);

    const handleSendMessage = async (content: string) => {
        // 添加用户消息
        addMessage(content, 'user', 'text');
        setIsLoading(true);

        try {
            const response = await fetch('/api/ai', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    userId,
                    articleId,
                    message: content
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'AI服务请求失败');
            }

            const data = await response.json();

            // 更新消息列表和动作按钮
            if (data.reply) {
                addMessage(data.reply.content, data.reply.role, data.reply.type);
            }
            setActions(data.actions || []);

        } catch (error) {
            console.error('Error:', error);
            addMessage('抱歉，我遇到了一些问题，请稍后再试。', 'assistant', 'text');
        } finally {
            setIsLoading(false);
        }
    };

    const handleAction = useCallback(async (action: ActionButton) => {
        try {
            setIsLoading(true);

            // 添加系统消息显示正在执行的动作
            const actionMessage = {
                id: Date.now().toString(),
                role: 'system' as const,
                content: `正在执行：${action.label}`,
                type: 'text',
                timestamp: new Date().toISOString()
            } satisfies Message;
            setMessages(prev => [...prev, actionMessage]);

            // 调用AI服务API执行动作
            const response = await fetch('/api/ai/action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    userId,
                    articleId,
                    actionId: action.id,
                    metadata: action.metadata
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || '执行操作失败');
            }

            const data = await response.json();

            // 更新消息列表和动作按钮
            if (data.message) {
                setMessages(prev => [...prev, data.message]);
            }
            setActions(data.actions || []);

        } catch (error) {
            console.error('Action Error:', error);
            const errorMessage = {
                id: Date.now().toString(),
                role: 'system' as const,
                content: error instanceof Error ? error.message : '执行操作时出现错误，请重试。',
                type: 'text',
                timestamp: new Date().toISOString()
            } satisfies Message;
            setMessages(prev => [...prev, errorMessage]);
            setActions([]);
        } finally {
            setIsLoading(false);
        }
    }, [userId, articleId]);

    return (
        <div className={`flex flex-col h-full ${className}`}>
            <div className="flex-1 min-h-0">
                <ChatInterface
                    messages={messages}
                    onSendMessage={handleSendMessage}
                    isLoading={isLoading}
                    onClearChat={handleClearChat}
                />
            </div>
            {actions.length > 0 && (
                <ActionButtons
                    actions={actions}
                    onAction={handleAction}
                    isLoading={isLoading}
                />
            )}
        </div>
    );
} 