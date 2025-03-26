import { NextRequest, NextResponse } from 'next/server';

// 模拟文章数据
let articles = [
  {
    id: '1',
    title: '人工智能简史',
    excerpt: '从图灵测试到GPT-4，人工智能的发展历程...',
    content: '人工智能（Artificial Intelligence，简称AI）的概念最早可以追溯到20世纪50年代...',
    status: 'published',
    category: '科技',
    tags: ['AI', '技术', '历史'],
    cover_image: 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485',
    author_id: '2',
    view_count: 328,
    created_at: '2023-02-15T08:30:00Z',
    updated_at: '2023-02-16T10:15:00Z',
    published_at: '2023-02-16T10:15:00Z',
  },
  {
    id: '2',
    title: '机器学习入门指南',
    excerpt: '从零开始学习机器学习的完整路径...',
    content: '机器学习是人工智能的一个分支，它允许计算机系统从数据中学习和改进，而无需明确编程...',
    status: 'published',
    category: '编程',
    tags: ['机器学习', '编程', '教程'],
    cover_image: 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb',
    author_id: '2',
    view_count: 215,
    created_at: '2023-03-05T14:20:00Z',
    updated_at: '2023-03-06T09:45:00Z',
    published_at: '2023-03-06T09:45:00Z',
  },
  {
    id: '3',
    title: 'Python数据分析基础',
    excerpt: '使用Python进行数据分析的基本技巧和工具...',
    content: 'Python已经成为数据分析领域最流行的编程语言之一，这主要归功于其丰富的库生态系统...',
    status: 'draft',
    category: '编程',
    tags: ['Python', '数据分析', '教程'],
    cover_image: 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935',
    author_id: '2',
    view_count: 0,
    created_at: '2023-04-10T11:05:00Z',
    updated_at: '2023-04-10T11:05:00Z',
    published_at: null,
  },
  {
    id: '4',
    title: '自然语言处理技术发展',
    excerpt: 'NLP技术的演进及其在现代AI中的应用...',
    content: '自然语言处理（NLP）是人工智能的一个子领域，专注于计算机与人类语言之间的交互...',
    status: 'draft',
    category: '科技',
    tags: ['NLP', 'AI', '技术'],
    cover_image: 'https://images.unsplash.com/photo-1518770660439-4636190af475',
    author_id: '2',
    view_count: 0,
    created_at: '2023-05-18T16:40:00Z',
    updated_at: '2023-05-18T16:40:00Z',
    published_at: null,
  },
  {
    id: '5',
    title: '深度学习框架比较',
    excerpt: 'TensorFlow、PyTorch和其他主流深度学习框架的对比分析...',
    content: '随着深度学习的普及，各种框架也如雨后春笋般涌现。本文将对当前最流行的几个深度学习框架进行比较...',
    status: 'published',
    category: '编程',
    tags: ['深度学习', 'TensorFlow', 'PyTorch'],
    cover_image: 'https://images.unsplash.com/photo-1558346490-a72e53ae2d4f',
    author_id: '2',
    view_count: 187,
    created_at: '2023-06-22T09:15:00Z',
    updated_at: '2023-06-23T14:30:00Z',
    published_at: '2023-06-23T14:30:00Z',
  }
];

// 获取特定文章
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const articleId = params.id;
    const article = articles.find(a => a.id === articleId);

    if (!article) {
      return NextResponse.json(
        { error: 'Article not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(article);
  } catch (error) {
    console.error('Error getting article:', error);
    return NextResponse.json(
      { error: 'Failed to get article' },
      { status: 500 }
    );
  }
}

// 更新文章
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const articleId = params.id;
    const articleIndex = articles.findIndex(a => a.id === articleId);

    if (articleIndex === -1) {
      return NextResponse.json(
        { error: 'Article not found' },
        { status: 404 }
      );
    }

    const body = await request.json();
    const oldArticle = articles[articleIndex];

    // 检查是否从草稿变为已发布状态
    const isPublishing = oldArticle.status === 'draft' && body.status === 'published';

    // 更新文章
    const updatedArticle = {
      ...oldArticle,
      ...body,
      id: articleId, // 确保ID不变
      updated_at: new Date().toISOString(),
      // 如果从草稿变为已发布，设置发布时间
      published_at: isPublishing ? new Date().toISOString() : oldArticle.published_at,
    };

    articles[articleIndex] = updatedArticle;

    return NextResponse.json(updatedArticle);
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
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const articleId = params.id;
    const articleIndex = articles.findIndex(a => a.id === articleId);

    if (articleIndex === -1) {
      return NextResponse.json(
        { error: 'Article not found' },
        { status: 404 }
      );
    }

    const deletedArticle = articles[articleIndex];
    articles = articles.filter(a => a.id !== articleId);

    return NextResponse.json({ success: true, article: deletedArticle });
  } catch (error) {
    console.error('Error deleting article:', error);
    return NextResponse.json(
      { error: 'Failed to delete article' },
      { status: 500 }
    );
  }
}
