'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthContext';
import UserLayout from '@/components/user/Layout';
import ArticleList from '@/components/user/articles/ArticleList';

export default function PublishedArticlesPage() {
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
      <div className="pt-6 px-1">
        <div className="mb-8">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
            已发布文章
          </h1>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700/50 shadow-sm">
          <ArticleList status="published" />
        </div>
      </div>
    </UserLayout>
  );
}