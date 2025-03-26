'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth/AuthContext';

interface DashboardStats {
  totalArticles: number;
  publishedArticles: number;
  draftArticles: number;
  totalViews: number;
  recentActivity: {
    id: string;
    title: string;
    type: 'created' | 'updated' | 'published';
    timestamp: string;
  }[];
}

// 图标组件
const ArticlesIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
  </svg>
);

const ViewsIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
  </svg>
);

const PlusIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
  </svg>
);

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalArticles: 0,
    publishedArticles: 0,
    draftArticles: 0,
    totalViews: 0,
    recentActivity: [],
  });
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  // 加载用户统计数据
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);

        // 获取所有文章
        const response = await fetch(`/api/user/articles?author_id=${user?.id}`);

        if (!response.ok) {
          throw new Error('获取文章失败');
        }

        const articles = await response.json();

        // 计算统计数据
        const published = articles.filter((article: any) => article.status === 'published');
        const drafts = articles.filter((article: any) => article.status === 'draft');
        const totalViews = published.reduce((sum: number, article: any) => sum + article.view_count, 0);

        // 处理最近活动
        const recentActivity: any[] = [];

        // 添加最近创建的文章
        const recentCreated = [...articles].sort(
          (a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        ).slice(0, 2);

        recentCreated.forEach((article: any) => {
          recentActivity.push({
            id: article.id,
            title: article.title,
            type: 'created',
            timestamp: article.created_at,
          });
        });

        // 添加最近发布的文章
        const recentPublished = [...published].sort(
          (a: any, b: any) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime()
        ).slice(0, 2);

        recentPublished.forEach((article: any) => {
          recentActivity.push({
            id: article.id,
            title: article.title,
            type: 'published',
            timestamp: article.published_at,
          });
        });

        // 添加最近更新的文章
        const recentUpdated = [...articles].sort(
          (a: any, b: any) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        ).slice(0, 2);

        recentUpdated.forEach((article: any) => {
          if (article.updated_at !== article.created_at) {
            recentActivity.push({
              id: article.id,
              title: article.title,
              type: 'updated',
              timestamp: article.updated_at,
            });
          }
        });

        // 按时间排序并限制数量
        recentActivity.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        recentActivity.splice(5);

        setStats({
          totalArticles: articles.length,
          publishedArticles: published.length,
          draftArticles: drafts.length,
          totalViews,
          recentActivity,
        });
      } catch (error) {
        console.error('加载统计数据出错:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user?.id) {
      fetchStats();
    }
  }, [user]);

  // 格式化日期
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      // 检查日期是否有效
      if (isNaN(date.getTime())) {
        return '日期无效';
      }
      return new Intl.DateTimeFormat('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (error) {
      return '日期无效';
    }
  };

  return (
    <div className="pt-20 sm:pt-24 lg:pt-16">
      <div className="mb-6">
        <h1 className="text-2xl font-medium text-gray-900 dark:text-white mb-1">
          {user?.email ? `欢迎回来，${user.email.split('@')[0]}` : '欢迎回来'}
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          这里是您最近的活动记录
        </p>
      </div>

      {/* 活动记录 */}
      <div>
        {/* 最近活动 */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">
              最近活动
            </h3>
            <Link
              href="/user/articles/new"
              className="inline-flex items-center gap-1 text-xs text-primary-600 dark:text-primary-400 hover:text-primary-500 transition-colors"
            >
              <PlusIcon />
              <span>创建文章</span>
            </Link>
          </div>
          {loading ? (
            <div className="text-center py-10">
              <div className="animate-spin rounded-full h-6 w-6 border-2 border-gray-200 dark:border-gray-700 border-t-primary-600 mx-auto"></div>
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">加载中...</p>
            </div>
          ) : stats.recentActivity.length > 0 ? (
            <div className="flow-root">
              <ul className="divide-y divide-gray-100 dark:divide-gray-700">
                {stats.recentActivity.map((activity, index) => (
                  <li key={`${activity.id}-${activity.type}-${activity.timestamp}-${index}`}
                    className="px-6 py-4 transition-colors hover:bg-gray-50 dark:hover:bg-gray-750">
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex items-center gap-3 min-w-0">
                        <span
                          className={`h-7 w-7 rounded-full flex items-center justify-center
                            ${activity.type === 'created'
                              ? 'bg-blue-50 text-blue-500 dark:bg-blue-900/20 dark:text-blue-400'
                              : activity.type === 'published'
                                ? 'bg-green-50 text-green-500 dark:bg-green-900/20 dark:text-green-400'
                                : 'bg-amber-50 text-amber-500 dark:bg-amber-900/20 dark:text-amber-400'
                            }`}
                        >
                          {activity.type === 'created' ? (
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                              />
                            </svg>
                          ) : activity.type === 'published' ? (
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M5 13l4 4L19 7"
                              />
                            </svg>
                          ) : (
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                              />
                            </svg>
                          )}
                        </span>
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {activity.title}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {activity.type === 'created'
                              ? '创建了文章'
                              : activity.type === 'published'
                                ? '发布了文章'
                                : '更新了文章'}
                          </p>
                        </div>
                      </div>
                      <div className="flex flex-col items-end">
                        <Link
                          href={`/user/articles/${activity.id}`}
                          className="text-xs font-medium text-primary-600 dark:text-primary-400 hover:text-primary-500 transition-colors"
                        >
                          查看
                        </Link>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {formatDate(activity.timestamp)}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="text-center py-10">
              <div className="mx-auto w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                <ArticlesIcon />
              </div>
              <p className="mt-2 text-sm text-gray-900 dark:text-white font-medium">暂无活动记录</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">创建您的第一篇文章开始创作之旅</p>
              <Link
                href="/user/articles/new"
                className="mt-4 inline-flex items-center justify-center px-4 py-2 border border-transparent text-xs font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-900"
              >
                创建文章
              </Link>
            </div>
          )}
          <div className="bg-gray-50 dark:bg-gray-750 px-6 py-3 flex justify-between items-center">
            <div className="text-xs">
              <Link
                href="/user/articles"
                className="font-medium text-primary-600 dark:text-primary-400 hover:text-primary-500 transition-colors"
              >
                查看全部文章
              </Link>
            </div>
            {!loading && stats.totalArticles > 0 && (
              <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                <ArticlesIcon />
                <span>文章：{stats.totalArticles}</span>
                <ViewsIcon />
                <span>总浏览：{stats.totalViews}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
