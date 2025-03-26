import { NextRequest, NextResponse } from 'next/server';
import { getArticleById, updateMockArticle, deleteMockArticle } from '@/lib/mock/articles';

// 格式化文章数据
const formatArticle = (article: any) => ({
    id: article.id,
    title: article.title,
    content: article.content,
    summary: article.summary,
    coverImage: article.coverImage,
    status: article.status,
    author_id: article.author.id,
    author: article.author,
    created_at: article.createdAt,
    updated_at: article.updatedAt,
    published_at: article.status === 'published' ? article.updatedAt : null,
    view_count: article.viewCount,
    tags: article.tags,
});

// 获取单个文章
export async function GET(
    request: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const { id } = await params;

    // 获取文章数据
    const article = getArticleById(id);

    if (!article) {
        return NextResponse.json(
            { error: `Article with ID ${id} not found` },
            { status: 404 }
        );
    }

    // 返回成功响应
    return NextResponse.json(formatArticle(article));
}

// 更新文章
export async function PUT(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const { id } = await params;
        const data = await request.json();

        // 更新文章
        const updatedArticle = updateMockArticle(id, data);

        if (!updatedArticle) {
            return NextResponse.json(
                { error: `Article with ID ${id} not found` },
                { status: 404 }
            );
        }

        return NextResponse.json(formatArticle(updatedArticle));
    } catch (error) {
        console.error('Error updating article:', error);
        return NextResponse.json(
            { error: 'Failed to update article' },
            { status: 500 }
        );
    }
}

// 删除文章
export async function DELETE(
    request: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    const { id } = await params;

    // 删除文章
    const success = deleteMockArticle(id);

    if (!success) {
        return NextResponse.json(
            { error: `Article with ID ${id} not found` },
            { status: 404 }
        );
    }

    return NextResponse.json({ success: true });
}
