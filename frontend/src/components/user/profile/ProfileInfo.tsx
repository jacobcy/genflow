'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth/AuthContext';

// 模拟的平台账号数据
const MOCK_PLATFORM_ACCOUNTS = [
    {
        id: 'baijiahao',
        name: '百家号',
        icon: (
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
        ),
        username: 'genflow_baijiahao',
        followers: '12.5k',
        articles: 45,
        status: 'active',
    },
    {
        id: 'sohu',
        name: '搜狐号',
        icon: (
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        ),
        username: 'genflow_sohu',
        followers: '8.3k',
        articles: 32,
        status: 'active',
    },
    {
        id: 'toutiao',
        name: '头条号',
        icon: (
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 3v2H6v14h12V5h-3V3h5v18H4V3h5z" />
            </svg>
        ),
        username: 'genflow_toutiao',
        followers: '15.2k',
        articles: 56,
        status: 'active',
    },
    {
        id: 'dayu',
        name: '大鱼号',
        icon: (
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" />
            </svg>
        ),
        username: 'genflow_dayu',
        followers: '6.8k',
        articles: 28,
        status: 'inactive',
    },
];

export default function ProfileInfo() {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('basic'); // 'basic' | 'platforms'

    return (
        <div>
            {/* 选项卡 */}
            <div className="px-6 py-3 bg-gray-50 dark:bg-gray-750 border-b border-gray-100 dark:border-gray-700">
                <div className="flex space-x-4">
                    <button
                        onClick={() => setActiveTab('basic')}
                        className={`px-3 py-2 text-sm font-medium rounded-md ${activeTab === 'basic'
                            ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
                            : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                            }`}
                    >
                        基本信息
                    </button>
                    <button
                        onClick={() => setActiveTab('platforms')}
                        className={`px-3 py-2 text-sm font-medium rounded-md ${activeTab === 'platforms'
                            ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
                            : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                            }`}
                    >
                        平台账号
                    </button>
                </div>
            </div>

            {/* 基本信息 */}
            {activeTab === 'basic' && (
                <div className="px-6 py-5 space-y-6">
                    <div className="flex items-center">
                        <div className="flex-shrink-0">
                            <div className="h-20 w-20 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-500 dark:text-gray-400">
                                <svg className="h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                            </div>
                        </div>
                        <div className="ml-6">
                            <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                                {user?.email?.split('@')[0]}
                            </h4>
                            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                                {user?.email}
                            </p>
                            <button className="mt-2 text-xs text-primary-600 dark:text-primary-400 hover:text-primary-500 transition-colors">
                                更换头像
                            </button>
                        </div>
                    </div>

                    <div className="border-t border-gray-100 dark:border-gray-700 pt-6">
                        <dl className="space-y-4">
                            <div>
                                <dt className="text-xs font-medium text-gray-500 dark:text-gray-400">
                                    用户名
                                </dt>
                                <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                                    {user?.email?.split('@')[0]}
                                </dd>
                            </div>
                            <div>
                                <dt className="text-xs font-medium text-gray-500 dark:text-gray-400">
                                    邮箱
                                </dt>
                                <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                                    {user?.email}
                                </dd>
                            </div>
                            <div>
                                <dt className="text-xs font-medium text-gray-500 dark:text-gray-400">
                                    注册时间
                                </dt>
                                <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                                    2024年3月1日
                                </dd>
                            </div>
                        </dl>
                    </div>
                </div>
            )}

            {/* 平台账号 */}
            {activeTab === 'platforms' && (
                <div className="px-6 py-5">
                    <div className="space-y-4">
                        {MOCK_PLATFORM_ACCOUNTS.map((account) => (
                            <div
                                key={account.id}
                                className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-750 rounded-lg"
                            >
                                <div className="flex items-center space-x-4">
                                    <div className="flex-shrink-0">
                                        <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-500 dark:text-gray-400">
                                            {account.icon}
                                        </div>
                                    </div>
                                    <div>
                                        <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                                            {account.name}
                                        </h4>
                                        <p className="text-xs text-gray-500 dark:text-gray-400">
                                            @{account.username}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center space-x-6">
                                    <div className="text-right">
                                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                                            {account.followers}
                                        </p>
                                        <p className="text-xs text-gray-500 dark:text-gray-400">
                                            粉丝数
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                                            {account.articles}
                                        </p>
                                        <p className="text-xs text-gray-500 dark:text-gray-400">
                                            文章数
                                        </p>
                                    </div>
                                    <div>
                                        <span
                                            className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${account.status === 'active'
                                                ? 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                                : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                                                }`}
                                        >
                                            {account.status === 'active' ? '已连接' : '未连接'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="mt-6">
                        <button
                            type="button"
                            className="w-full flex items-center justify-center px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
                        >
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                            </svg>
                            添加新平台
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
