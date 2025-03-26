'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthContext';
import UserLayout from '@/components/user/Layout';
import ArticleView from '@/components/user/articles/ArticleView';
import { getArticle } from '@/lib/api/articles';
import { use } from 'react';

export default function ArticleDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { isAuthenticated, user, loading } = useAuth();
  const router = useRouter();
  const [article, setArticle] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // 加载文章数据
  useEffect(() => {
    console.log("加载文章数据useEffect执行", { isAuthenticated, loading, id, user });

    if (id) {
      setIsLoading(true);
      getArticle(id)
        .then((data) => {
          console.log("文章数据获取成功", data);
          setArticle(data);
          setIsLoading(false);
        })
        .catch((err) => {
          console.error("文章获取失败", err);
          setError('加载文章失败: ' + err.message);
          setIsLoading(false);
        });
    }
  }, [id]);

  // 未登录显示明确的未登录提示，而不是空白页或无限加载
  if (!loading && !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center p-6">
          <h2 className="mb-2 text-xl font-medium text-gray-900 dark:text-white">需要登录</h2>
          <p className="mb-5 text-sm text-gray-600 dark:text-gray-400">您需要登录才能查看此文章</p>
          <div className="flex space-x-4 justify-center">
            <button
              onClick={() => router.push('/login')}
              className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-gray-900 hover:bg-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600"
            >
              前往登录
            </button>
            {process.env.NODE_ENV === 'development' && (
              <button
                onClick={() => {
                  // @ts-ignore - 开发环境全局变量
                  if (window.__GENFLOW_AUTH_TOOLS?.mockLogin) {
                    // @ts-ignore
                    window.__GENFLOW_AUTH_TOOLS.mockLogin('user');
                  } else {
                    alert('开发工具未初始化，请刷新页面后重试');
                  }
                }}
                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                开发模式登录
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // 如果是管理员，提示应该去管理员界面
  if (!loading && isAuthenticated && user?.role !== 'user') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center p-6">
          <h2 className="mb-2 text-xl font-medium text-gray-900 dark:text-white">访问受限</h2>
          <p className="mb-5 text-sm text-gray-600 dark:text-gray-400">管理员账号应该访问管理员界面</p>
          <button
            onClick={() => router.push('/admin/dashboard')}
            className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-gray-900 hover:bg-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600"
          >
            前往管理界面
          </button>
        </div>
      </div>
    );
  }

  if (loading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin h-5 w-5 border-t border-gray-900 dark:border-gray-100 mx-auto"></div>
          <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">加载中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <UserLayout>
        <div className="p-4 bg-red-50 dark:bg-red-900/10 border-l-2 border-red-500" role="alert">
          <div className="flex">
            <div className="flex-1">
              <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
              {process.env.NODE_ENV === 'development' && (
                <div className="mt-3">
                  <button
                    onClick={() => window.location.reload()}
                    className="text-sm text-red-700 dark:text-red-400 hover:text-red-600 dark:hover:text-red-300"
                  >
                    刷新页面
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </UserLayout>
    );
  }

  return (
    <UserLayout>
      <div className="pt-6 px-1">
        <div className="max-w-5xl mx-auto">
          {/* 面包屑导航 */}
          <nav className="mb-6">
            <ol className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
              <li>
                <a href="/" className="hover:text-gray-900 dark:hover:text-white transition-colors">首页</a>
              </li>
              <li>
                <span className="mx-2">/</span>
              </li>
              <li>
                <a href="/user/articles" className="hover:text-gray-900 dark:hover:text-white transition-colors">全部文章</a>
              </li>
            </ol>
          </nav>

          {/* 文章内容 */}
          {article && <ArticleView article={article} />}
        </div>
      </div>
    </UserLayout>
  );
}
