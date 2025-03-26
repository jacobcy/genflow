import React, { useState, useRef, useEffect } from 'react';
import { Message } from '@/types/common';
import ReactMarkdown from 'react-markdown';
import type { Components } from 'react-markdown';

interface ChatInterfaceProps {
    messages: Message[];
    onSendMessage: (content: string) => void;
    isLoading?: boolean;
    onClearChat?: () => void;
}

export default function ChatInterface({
    messages,
    onSendMessage,
    isLoading = false,
    onClearChat
}: ChatInterfaceProps) {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // 自动滚动到最新消息
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // 自动调整输入框高度
    const adjustTextareaHeight = () => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`; // 限制最大高度为 120px
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim() && !isLoading) {
            onSendMessage(input.trim());
            setInput('');
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const markdownComponents: Components = {
        code: ({ children, className, node, ...props }) => {
            const match = /language-(\w+)/.exec(className || '');
            const isInline = !match;
            return (
                <code
                    className={`${className || ''} ${isInline
                        ? 'bg-gray-200 dark:bg-gray-600 rounded px-1'
                        : 'block bg-gray-800 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto'
                        }`}
                    {...props}
                >
                    {children}
                </code>
            );
        }
    };

    return (
        <div className="h-full flex flex-col overflow-hidden">
            {/* 顶部工具栏 */}
            <div className="flex-none px-4 py-2 border-b border-gray-200/60 dark:border-gray-700/40 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
                <div className="flex items-center justify-between">
                    <h2 className="text-sm font-medium text-gray-900 dark:text-white truncate">AI 助手</h2>
                    {messages.length > 0 && (
                        <button
                            onClick={onClearChat}
                            className="flex-none ml-2 text-xs px-2 py-1 rounded text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors"
                        >
                            清除对话
                        </button>
                    )}
                </div>
            </div>

            {/* 消息列表区域 - 只有这里可以滚动 */}
            <div className="flex-1 overflow-y-auto overflow-x-hidden">
                {messages.length === 0 ? (
                    <div className="h-full flex items-center justify-center">
                        <p className="text-gray-500 dark:text-gray-400">开始对话吧...</p>
                    </div>
                ) : (
                    <div className="px-4 py-4 space-y-4">
                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[80%] rounded-lg p-3 ${message.role === 'user'
                                        ? 'bg-primary-100 dark:bg-primary-900 text-primary-900 dark:text-primary-100'
                                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                                        } shadow-sm break-words`}
                                >
                                    {message.type === 'markdown' ? (
                                        <div className="prose dark:prose-invert max-w-none">
                                            <ReactMarkdown components={markdownComponents}>
                                                {message.content}
                                            </ReactMarkdown>
                                        </div>
                                    ) : (
                                        <p className="whitespace-pre-wrap">{message.content}</p>
                                    )}
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* 输入区域 - 固定高度 */}
            <div className="flex-none border-t border-gray-200/60 dark:border-gray-700/40">
                <form onSubmit={handleSubmit} className="px-4 py-2">
                    <div className="relative">
                        <textarea
                            ref={textareaRef}
                            value={input}
                            onChange={(e) => {
                                setInput(e.target.value);
                                adjustTextareaHeight();
                            }}
                            onKeyDown={handleKeyDown}
                            placeholder="输入消息..."
                            className="w-full px-4 py-2 pr-24 text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white resize-none min-h-[40px] max-h-[120px] bg-white/80 dark:bg-gray-700/80 backdrop-blur-sm border border-gray-200/60 dark:border-gray-700/40"
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={isLoading || !input.trim()}
                            className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isLoading ? (
                                <div className="flex items-center space-x-2">
                                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                    <span>思考中...</span>
                                </div>
                            ) : (
                                '发送'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
