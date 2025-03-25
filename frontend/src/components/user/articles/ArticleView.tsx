'use client';

import React from 'react';
import { format } from 'date-fns';
import DOMPurify from 'isomorphic-dompurify';

// 添加一个安全的日期格式化函数
const formatDate = (dateString: string) => {
  try {
    const date = new Date(dateString);
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      return '日期无效';
    }
    return format(date, 'yyyy-MM-dd HH:mm');
  } catch (error) {
    return '日期无效';
  }
};

interface Article {
  id: string;
  title: string;
  content: string;
  summary: string;
  coverImage?: string;
  status: 'draft' | 'published';
  author: {
    id: string;
    name: string;
    avatar?: string;
  };
  createdAt: string;
  updatedAt: string;
  viewCount: number;
  tags: string[];
}

interface ArticleViewProps {
  article: Article;
}

export default function ArticleView({ article }: ArticleViewProps) {
  // 清理HTML内容，防止XSS攻击
  const sanitizedContent = DOMPurify.sanitize(article.content);

  return (
    <div className="bg-white dark:bg-gray-800">
      <div className="max-w-4xl mx-auto py-8 px-6">
        {/* 标题区域 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            {article.title || '(无标题)'}
          </h1>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
              <span>{article.status === 'published' ? '已发布' : '草稿'}</span>
              <span>·</span>
              <span>更新于 {formatDate(article.updatedAt)}</span>
              <span>·</span>
              <span>{article.viewCount} 次阅读</span>
            </div>
            {article.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {article.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm text-gray-500 dark:text-gray-400"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 封面图 */}
        {article.coverImage && (
          <div className="relative w-full mb-8 rounded-lg overflow-hidden aspect-[21/9]">
            <img
              src={article.coverImage}
              alt={article.title}
              className="absolute inset-0 w-full h-full object-cover"
            />
          </div>
        )}

        {/* 摘要 */}
        {article.summary && (
          <div className="mb-8">
            <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
              {article.summary}
            </p>
          </div>
        )}

        {/* 分割线 */}
        <div className="my-8 border-t border-gray-100 dark:border-gray-800"></div>

        {/* 文章内容 */}
        <div className="prose prose-lg dark:prose-invert prose-headings:font-medium prose-a:text-primary-600 dark:prose-a:text-primary-400 max-w-none">
          <div
            dangerouslySetInnerHTML={{ __html: sanitizedContent }}
            className="prose-h1:text-3xl prose-h2:text-2xl prose-h3:text-xl prose-p:text-base prose-p:leading-relaxed prose-li:text-base prose-strong:text-gray-900 dark:prose-strong:text-white prose-em:text-gray-700 dark:prose-em:text-gray-300 prose-code:text-primary-600 dark:prose-code:text-primary-400 prose-pre:bg-gray-50 dark:prose-pre:bg-gray-900/50 prose-pre:border prose-pre:border-gray-100 dark:prose-pre:border-gray-800 prose-pre:rounded-xl prose-blockquote:border-l-4 prose-blockquote:border-gray-200 dark:prose-blockquote:border-gray-700 prose-blockquote:pl-6 prose-blockquote:italic prose-blockquote:text-gray-700 dark:prose-blockquote:text-gray-300"
          />
        </div>
      </div>
    </div>
  );
}