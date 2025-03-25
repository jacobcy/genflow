'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthContext';
import UserLayout from '@/components/user/Layout';
import ProfileInfo from '@/components/user/profile/ProfileInfo';

export default function ProfilePage() {
    const { isAuthenticated, user, loading } = useAuth();
    const router = useRouter();

    // 身份验证检查
    useEffect(() => {
        if (!loading && !isAuthenticated) {
            router.push('/login');
        } else if (!loading && isAuthenticated && user?.role !== 'user') {
            router.push('/admin/dashboard');
        }
    }, [isAuthenticated, user, loading, router]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
                <div className="text-center">
                    <div className="animate-spin h-5 w-5 border-t border-gray-900 dark:border-gray-100 mx-auto"></div>
                    <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">加载中...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated || user?.role !== 'user') {
        return null;
    }

    return (
        <UserLayout>
            <div className="pt-6">
                <div className="mb-6">
                    <h1 className="text-2xl font-medium text-gray-900 dark:text-white">
                        个人信息
                    </h1>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
                    <ProfileInfo />
                    <div className="px-6 py-4 border-t border-gray-100 dark:border-gray-700 flex justify-end">
                        <button
                            type="button"
                            className="inline-flex items-center gap-1 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-500 transition-colors"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                            <span>编辑信息</span>
                        </button>
                    </div>
                </div>
            </div>
        </UserLayout>
    );
} 