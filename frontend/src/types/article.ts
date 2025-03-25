import { BaseMetadata, Position, DocumentFormat } from './common';

/**
 * 文章状态
 * @description 定义文章的发布状态
 */
export type ArticleStatus = 'draft' | 'published' | 'archived' | 'deleted';

/**
 * 文章元数据
 * @description 定义文章的元数据信息
 */
export interface ArticleMetadata extends BaseMetadata {
    wordCount: number;
    readingTime: number;
    lastModified: string;
    author: string;
    status: ArticleStatus;
    tags: string[];
    category?: string;
    cover?: {
        url: string;
        alt?: string;
        source?: string;
    };
}

/**
 * 文章选区
 * @description 定义文章内容的选择区域
 */
export interface Selection extends Position {
    content: string;
}

/**
 * 文章状态
 * @description 定义文章的完整状态结构
 */
export interface ArticleState {
    id: string;
    title: string;
    content: string;
    version: string;
    format: DocumentFormat;
    metadata: ArticleMetadata;
    cursor?: Position;
    selection?: Selection;
    outline?: Array<{
        level: number;
        title: string;
        position: Position;
    }>;
    summary?: string;
    references?: Array<{
        id: string;
        title: string;
        url: string;
        type: 'article' | 'book' | 'website';
    }>;
}

/**
 * 文章分析结果
 * @description 定义文章的分析指标和建议
 */
export interface ArticleAnalysis {
    metrics: {
        readability: number;
        coherence: number;
        engagement: number;
        seo: number;
        [key: string]: number;
    };
    suggestions: Array<{
        type: 'style' | 'content' | 'structure' | 'seo';
        description: string;
        priority: 'high' | 'medium' | 'low';
        position?: Position;
        recommendation?: string;
    }>;
    keywords: Array<{
        word: string;
        frequency: number;
        density: number;
    }>;
}

/**
 * 文章历史记录
 * @description 定义文章的修改历史
 */
export interface ArticleHistory {
    version: string;
    timestamp: string;
    author: string;
    changes: Array<{
        type: 'insert' | 'delete' | 'replace' | 'format';
        position: Position;
        content?: string;
        metadata?: {
            reason?: string;
            source?: 'user' | 'ai' | 'system';
            [key: string]: any;
        };
    }>;
}

/**
 * 文章导出选项
 * @description 定义文章导出的配置选项
 */
export interface ExportOptions {
    format: DocumentFormat;
    includeMetadata: boolean;
    includeCover: boolean;
    includeOutline: boolean;
    includeSummary: boolean;
    includeReferences: boolean;
    styles?: {
        font?: string;
        fontSize?: number;
        lineHeight?: number;
        [key: string]: any;
    };
} 