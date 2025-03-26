import { useState } from 'react';
import AIAssistant from './AIAssistant';

interface AISidebarProps {
    userId: string;
    articleId?: string;
    showByDefault?: boolean;
    className?: string;
}

export default function AISidebar({
    userId,
    articleId = 'default',
    showByDefault = true,
    className = ''
}: AISidebarProps) {
    const [showAIAssistant, setShowAIAssistant] = useState(showByDefault);

    return (
        <div className="fixed top-0 right-0 bottom-0 flex z-30">
            {/* AI助手内容 */}
            <div
                className={`relative flex flex-col bg-gradient-to-l from-gray-50/95 to-white/80 dark:from-gray-900 dark:to-gray-800/90 backdrop-blur-sm border-l border-gray-200/60 dark:border-gray-700/40 transform transition-all duration-300 ease-in-out ${showAIAssistant ? 'w-[40vw]' : 'w-20'
                    } ${className}`}
            >
                {/* 折叠按钮 */}
                <button
                    type="button"
                    onClick={() => setShowAIAssistant(!showAIAssistant)}
                    className="absolute top-1/2 -translate-y-1/2 left-0 -ml-3 h-8 w-8 rounded-full bg-white/90 dark:bg-gray-800 border border-gray-200/60 dark:border-gray-700/40 flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-750 focus:outline-none focus:ring-2 focus:ring-primary-500/50 dark:focus:ring-offset-gray-900 z-50 backdrop-blur-sm"
                >
                    <svg
                        className={`h-5 w-5 transform transition-transform duration-300 ease-in-out ${showAIAssistant ? 'rotate-180' : ''}`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                    </svg>
                </button>

                {/* 折叠时显示的标题 */}
                <div className={`flex-1 flex flex-col overflow-hidden pt-16`}>
                    <div className={`absolute top-6 left-0 w-20 flex items-center justify-center transition-opacity duration-300 ${showAIAssistant ? 'opacity-0' : 'opacity-100'}`}>
                        <span className="text-gray-500 dark:text-gray-400 text-sm font-medium vertical-text">AI 助手</span>
                    </div>

                    <div className={`flex-1 flex flex-col min-h-0 transition-opacity duration-300 ${showAIAssistant ? 'opacity-100' : 'opacity-0'}`}>
                        <AIAssistant
                            userId={userId}
                            articleId={articleId}
                            className="flex-1 flex flex-col min-h-0"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
