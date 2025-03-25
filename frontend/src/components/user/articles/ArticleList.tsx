'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { format } from 'date-fns';
import { useAuth } from '@/lib/auth/AuthContext';
import { getUserArticles, deleteArticle } from '@/lib/api/articles';
import { toast } from 'react-hot-toast';

interface Article {
  id: string;
  title: string;
  status: 'draft' | 'published';
  createdAt: string;
  updatedAt: string;
  viewCount: number;
}

interface ArticleListProps {
  status: 'draft' | 'published' | 'all';
}

// 添加一个安全的日期格式化函数
const formatDate = (dateString: string) => {
  try {
    const date = new Date(dateString);
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      return '日期无效';
    }
    return format(date, 'yyyy-MM-dd HH:mm');
  } catch (error: unknown) {
    return '日期无效';
  }
};

export default function ArticleList({ status }: ArticleListProps) {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    if (user?.id) {
      setLoading(true);
      getUserArticles(status)
        .then((data) => {
          setArticles(data);
          setLoading(false);
        })
        .catch((err: unknown) => {
          const errorMessage = err instanceof Error ? err.message : '获取文章列表失败';
          setError(errorMessage);
          setLoading(false);
        });
    }
  }, [user, status]);

  const handleDelete = async (id: string) => {
    if (confirm('确定要删除这篇文章吗？此操作不可撤销。')) {
      try {
        await deleteArticle(id);
        setArticles(articles.filter((article) => article.id !== id));
        toast.success('文章已删除');
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : '未知错误';
        toast.error('删除文章失败: ' + errorMessage);
      }
    }
  };

  if (loading) {
    return (
      <div className="py-8">
        <div className="animate-pulse flex space-x-4">
          <div className="flex-1 space-y-6 py-1">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">错误!</strong>
        <span className="block sm:inline"> {error}</span>
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="text-center py-10">
        <svg
          className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">没有{status === 'draft' ? '草稿' : '已发布文章'}</h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">现在就开始创建一篇新文章吧！</p>
        <div className="mt-6">
          <Link href="/user/articles/new">
            <span className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-900">
              新建文章
            </span>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              标题
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              状态
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              创建日期
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              最后更新
            </th>
            {status === 'published' && (
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                阅读量
              </th>
            )}
            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              操作
            </th>
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
          {articles.map((article) => (
            <tr key={article.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {article.status === 'published' ? (
                    <Link href={`/user/articles/${article.id}`}>
                      {article.title || '(无标题)'}
                    </Link>
                  ) : (
                    <Link href={`/user/articles/${article.id}/edit`}>
                      {article.title || '(无标题)'}
                    </Link>
                  )}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${article.status === 'published'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    }`}
                >
                  {article.status === 'published' ? '已发布' : '草稿'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {formatDate(article.createdAt)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {formatDate(article.updatedAt)}
              </td>
              {status === 'published' && (
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {article.viewCount}
                </td>
              )}
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div className="flex justify-end space-x-3">
                  {article.status === 'draft' ? (
                    // 草稿显示编辑和删除按钮
                    <>
                      <Link href={`/user/articles/${article.id}/edit`}>
                        <span className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">
                          编辑
                        </span>
                      </Link>
                      <button
                        onClick={() => handleDelete(article.id)}
                        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                      >
                        删除
                      </button>
                    </>
                  ) : (
                    // 已发布文章显示查看和删除按钮
                    <>
                      <Link href={`/user/articles/${article.id}`}>
                        <span className="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300">
                          查看
                        </span>
                      </Link>
                      <button
                        onClick={() => handleDelete(article.id)}
                        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                      >
                        删除
                      </button>
                    </>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}