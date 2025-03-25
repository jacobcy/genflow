import { NextRequest, NextResponse } from 'next/server';
import { getAllArticles, createMockArticle } from '@/lib/mock/articles';

// 获取所有文章
export async function GET() {
    const articles = getAllArticles();

    // 转换字段格式，保持API一致性
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

    return NextResponse.json(formattedArticles);
}

// 创建新文章
export async function POST(request: NextRequest) {
    try {
        const articleData = await request.json();

        // 创建新文章
        const newArticle = createMockArticle(articleData);

        // 转换响应格式
        const formattedArticle = {
            id: newArticle.id,
            title: newArticle.title,
            content: newArticle.content,
            summary: newArticle.summary,
            cover_image: newArticle.coverImage,
            status: newArticle.status,
            author_id: newArticle.author.id,
            author: newArticle.author,
            created_at: newArticle.createdAt,
            updated_at: newArticle.updatedAt,
            published_at: newArticle.status === 'published' ? newArticle.updatedAt : null,
            view_count: newArticle.viewCount,
            tags: newArticle.tags,
        };

        return NextResponse.json(formattedArticle, { status: 201 });
    } catch (error) {
        console.error('Error creating article:', error);
        return NextResponse.json(
            { error: 'Failed to create article' },
            { status: 500 }
        );
    }
} 