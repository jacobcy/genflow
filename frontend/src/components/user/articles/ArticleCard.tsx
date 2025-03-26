'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface ArticleCardProps {
  article: {
    id: string;
    title: string;
    excerpt: string;
    status: string;
    category: string;
    tags: string[];
    cover_image: string;
    created_at: string;
    updated_at: string;
    published_at: string | null;
    view_count: number;
  };
  onDelete?: (id: string) => void;
}

export default function ArticleCard({ article, onDelete }: ArticleCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const router = useRouter();

  // 格式化日期
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '未发布';

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

  // 编辑文章
  const handleEdit = () => {
    router.push(`/user/articles/edit/${article.id}`);
  };

  // 删除文章
  const handleDelete = async () => {
    if (!window.confirm(`确定要删除文章"${article.title}"吗？`)) {
      return;
    }

    try {
      setIsDeleting(true);

      const response = await fetch(`/api/user/articles/${article.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('删除文章失败');
      }

      if (onDelete) {
        onDelete(article.id);
      }
    } catch (error) {
      console.error('删除文章出错:', error);
      alert('删除文章失败，请重试');
    } finally {
      setIsDeleting(false);
    }
  };

  // 发布文章
  const handlePublish = async () => {
    if (article.status === 'published') return;

    try {
      const response = await fetch(`/api/user/articles/${article.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: 'published',
        }),
      });

      if (!response.ok) {
        throw new Error('发布文章失败');
      }

      router.refresh();
    } catch (error) {
      console.error('发布文章出错:', error);
      alert('发布文章失败，请重试');
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
      {/* 文章封面图 */}
      <div className="relative h-48 w-full overflow-hidden">
        <img
          src={article.cover_image || 'https://images.unsplash.com/photo-1629654297299-c8506221ca97?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=500&q=80'}
          alt={article.title}
          className="h-48 w-full object-cover transition-all hover:scale-105"
        />
        <div className="absolute top-2 right-2">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${article.status === 'published'
            ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
            }`}>
            {article.status === 'published' ? '已发布' : '草稿'}
          </span>
        </div>
      </div>

      {/* 文章内容 */}
      <div className="p-5">
        <Link href={`/user/articles/${article.id}`}>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white hover:text-primary-600 dark:hover:text-primary-400 transition">
            {article.title}
          </h3>
        </Link>

        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
          {article.excerpt}
        </p>

        {/* 分类和标签 */}
        <div className="mt-4 flex flex-wrap gap-2">
          {article.category && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
              {article.category}
            </span>
          )}

          {article.tags.map((tag, index) => (
            <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
              {tag}
            </span>
          ))}
        </div>

        {/* 底部信息栏 */}
        <div className="mt-4 flex justify-between items-center">
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {article.status === 'published' ? (
              <>
                <span>发布于: {formatDate(article.published_at)}</span>
                <span className="mx-2">•</span>
                <span>阅读: {article.view_count}</span>
              </>
            ) : (
              <>
                <span>创建于: {formatDate(article.created_at)}</span>
                <span className="mx-2">•</span>
                <span>更新于: {formatDate(article.updated_at)}</span>
              </>
            )}
          </div>

          {/* 操作按钮 */}
          <div className="flex space-x-2">
            <button
              onClick={handleEdit}
              className="text-sm text-gray-600 hover:text-primary-600 dark:text-gray-300 dark:hover:text-primary-400"
            >
              编辑
            </button>

            {article.status === 'draft' && (
              <button
                onClick={handlePublish}
                className="text-sm text-gray-600 hover:text-green-600 dark:text-gray-300 dark:hover:text-green-400"
              >
                发布
              </button>
            )}

            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="text-sm text-gray-600 hover:text-red-600 dark:text-gray-300 dark:hover:text-red-400 disabled:opacity-50"
            >
              {isDeleting ? '删除中...' : '删除'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
