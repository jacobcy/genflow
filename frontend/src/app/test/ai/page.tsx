'use client';

import { useState, useEffect } from 'react';
import AIAssistant from '@/components/ai/AIAssistant';
import UserLayout from '@/components/user/Layout';

interface HotSearchItem {
    title: string;
    url: string;
}

export default function AITestPage() {
    const [showAIAssistant, setShowAIAssistant] = useState(true);
    const [baiduHotSearches, setBaiduHotSearches] = useState<HotSearchItem[]>([]);

    useEffect(() => {
        // 获取百度热搜
        fetch('https://api2.firefoxchina.cn/homepage/3139.json')
            .then(res => res.json())
            .then(data => {
                if (data.data && data.data.data) {
                    setBaiduHotSearches(data.data.data);
                }
            })
            .catch(error => console.error('获取百度热搜失败:', error));
    }, []);

    return (
        <UserLayout>
            <div className="flex h-[calc(100vh-64px)]">
                {/* 主要内容区域 */}
                <div className={`flex-1 min-w-0 transition-all duration-300 ${showAIAssistant ? 'mr-[calc(100vw*0.4)]' : ''}`}>
                    <div className="h-full pt-6 px-6 overflow-y-auto">
                        <h1 className="text-xl font-semibold text-gray-900 dark:text-white mb-8">
                            实时热搜
                        </h1>

                        {/* 热搜内容 */}
                        <div className="max-w-2xl">
                            {/* 百度热搜 */}
                            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                                    <svg className="w-5 h-5 mr-2" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M580.585 105.792c-79.067-76.8-198.4-74.533-275.2 2.134-76.8 76.8-74.533 198.4 2.134 275.2l76.8 74.533 275.2-275.2-78.934-76.667z m-196.266 76.8c38.4-38.4 98.133-38.4 136.533 0l8.534 8.533L392.585 328.858l-8.533-8.533c-38.4-38.4-38.4-98.133 0-136.533l0.267-1.2z" fill="currentColor" />
                                        <path d="M866.585 391.792L531.318 727.058l-76.8-74.533-275.2 275.2 76.8 74.533c79.067 76.8 198.4 74.533 275.2-2.133 76.8-76.8 74.533-198.4-2.133-275.2l76.8-74.534 334.933-334.933-74.533-76.8v103.134z m-531.2 531.2c-38.4 38.4-98.133 38.4-136.533 0l-8.533-8.534 136.533-136.533 8.533 8.534c38.4 38.4 38.4 98.133 0 136.533z" fill="currentColor" />
                                    </svg>
                                    百度热搜
                                </h2>
                                <div className="space-y-3">
                                    {baiduHotSearches.slice(0, 10).map((item, index) => (
                                        <a
                                            key={index}
                                            href={item.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="flex items-center group hover:bg-gray-50 dark:hover:bg-gray-700 p-2 rounded-md transition-colors"
                                        >
                                            <span className={`w-6 h-6 flex items-center justify-center rounded-full ${index < 3 ? 'bg-red-500' : 'bg-gray-200 dark:bg-gray-600'} text-white text-sm mr-3`}>
                                                {index + 1}
                                            </span>
                                            <span className="text-gray-700 dark:text-gray-300 group-hover:text-primary-600 dark:group-hover:text-primary-400">
                                                {item.title}
                                            </span>
                                        </a>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* AI助手侧边栏 */}
                <div className="fixed top-[64px] right-0 bottom-0 flex z-30">
                    {/* AI助手内容 */}
                    <div
                        className={`relative flex flex-col bg-gradient-to-l from-gray-50/95 to-white/80 dark:from-gray-900 dark:to-gray-800/90 backdrop-blur-sm border-l border-gray-200/60 dark:border-gray-700/40 transform transition-all duration-300 ${showAIAssistant ? 'w-[calc(100vw*0.4)]' : 'w-20'}`}
                    >
                        {/* 折叠按钮 */}
                        <button
                            type="button"
                            onClick={() => setShowAIAssistant(!showAIAssistant)}
                            className="absolute top-1/2 -translate-y-1/2 left-0 -ml-3 h-8 w-8 rounded-full bg-white/90 dark:bg-gray-800 border border-gray-200/60 dark:border-gray-700/40 flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-750 focus:outline-none focus:ring-2 focus:ring-primary-500/50 dark:focus:ring-offset-gray-900 z-50 backdrop-blur-sm"
                        >
                            <svg
                                className={`h-5 w-5 transform transition-transform ${showAIAssistant ? 'rotate-180' : ''}`}
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                            </svg>
                        </button>

                        {/* 折叠时显示的标题 */}
                        <div className={`flex-1 flex flex-col pt-24 pb-4 overflow-y-auto`}>
                            <div className={`absolute top-6 left-0 w-20 flex items-center justify-center transition-opacity duration-300 ${showAIAssistant ? 'opacity-0' : 'opacity-100'}`}>
                                <span className="text-gray-500 dark:text-gray-400 text-sm font-medium vertical-text">AI 助手</span>
                            </div>

                            <div className={`flex-1 flex flex-col min-h-0 transition-opacity duration-300 ${showAIAssistant ? 'opacity-100' : 'opacity-0'}`}>
                                <AIAssistant
                                    userId="test-user"
                                    className="flex-1 flex flex-col min-h-0"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </UserLayout>
    );
}
