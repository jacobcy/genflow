import { NextRequest, NextResponse } from 'next/server';
import { getArticlesByStatus } from '@/lib/mock/articles';

export async function GET(request: NextRequest) {
  // 从URL参数中获取状态
  const searchParams = request.nextUrl.searchParams;
  const status = searchParams.get('status') as 'draft' | 'published' | 'all' || 'all';

  // 获取指定状态的文章
  const articles = getArticlesByStatus(status);

  // 转换字段格式，将驼峰命名法转换为下划线命名法
  const formattedArticles = articles.map(article => ({
    id: article.id,
    title: article.title,
    content: article.content,
    summary: article.summary,
    cover_image: article.coverImage,
    status: article.status,
    author_id: article.author.id,
    author: article.author,
    created_at: article.createdAt,
    updated_at: article.updatedAt,
    published_at: article.status === 'published' ? article.updatedAt : null,
    view_count: article.viewCount,
    tags: article.tags,
  }));

  // 返回成功响应
  return NextResponse.json(formattedArticles);
}
