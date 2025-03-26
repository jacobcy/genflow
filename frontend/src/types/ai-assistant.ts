import { WritingStage, Message, Priority, Position, DocumentFormat } from './common';

/**
 * AI 助手状态
 * @description 定义 AI 助手的运行状态
 */
export interface AIAssistantState {
    sessionId: string;
    stage: WritingStage;
    status: 'idle' | 'processing' | 'waiting';
    progress: number;
    suggestions: Array<{
        id: string;
        type: 'style' | 'content' | 'structure';
        content: string;
        priority: Priority;
        applied: boolean;
    }>;
    history: Array<Message>;
    context?: {
        title?: string;
        keywords?: string[];
        outline?: string;
        content?: string;
        [key: string]: any;
    };
}

/**
 * AI 助手可执行的操作类型
 * @description 定义 AI 助手支持的所有操作类型
 */
export type AIActionType =
    | 'SET_TITLE'           // 设置标题
    | 'SET_CONTENT'         // 设置全文内容
    | 'UPDATE_CONTENT'      // 更新部分内容
    | 'SET_SUMMARY'         // 设置摘要
    | 'SET_TAGS'           // 设置标签
    | 'SET_COVER'          // 设置封面图片
    | 'REPLACE_SECTION'     // 替换特定段落
    | 'OPTIMIZE_SECTION'    // 优化特定段落
    | 'GENERATE_OUTLINE'    // 生成大纲
    | 'SUGGEST_TAGS'       // 推荐标签
    | 'POLISH_WRITING'     // 润色文章
    | 'CHECK_GRAMMAR'      // 语法检查
    | 'TRANSLATE_SECTION'; // 翻译段落

/**
 * AI 助手函数的基础接口
 * @description 定义 AI 助手函数的基本结构
 */
export interface AIAssistantFunction {
    type: AIActionType;
    execute: boolean;        // 是否自动执行
    requireApproval: boolean; // 是否需要用户确认
}

/**
 * 设置标题
 */
export interface SetTitleFunction extends AIAssistantFunction {
    type: 'SET_TITLE';
    payload: {
        title: string;
        reason?: string;      // 修改原因
    };
}

/**
 * 设置内容
 */
export interface SetContentFunction extends AIAssistantFunction {
    type: 'SET_CONTENT';
    payload: {
        content: string;
        format: DocumentFormat;
    };
}

/**
 * 更新部分内容
 */
export interface UpdateContentFunction extends AIAssistantFunction {
    type: 'UPDATE_CONTENT';
    payload: {
        content: string;
        position: Position | {
            selector: string;   // CSS选择器
        };
    };
}

/**
 * 设置摘要
 */
export interface SetSummaryFunction extends AIAssistantFunction {
    type: 'SET_SUMMARY';
    payload: {
        summary: string;
        language?: string;    // 摘要语言
    };
}

/**
 * 设置标签
 */
export interface SetTagsFunction extends AIAssistantFunction {
    type: 'SET_TAGS';
    payload: {
        tags: string[];
        confidence?: number;  // AI 对标签的确信度
    };
}

/**
 * 设置封面图片
 */
export interface SetCoverFunction extends AIAssistantFunction {
    type: 'SET_COVER';
    payload: {
        url: string;
        alt?: string;
        source?: string;     // 图片来源
    };
}

/**
 * 替换段落
 */
export interface ReplaceSectionFunction extends AIAssistantFunction {
    type: 'REPLACE_SECTION';
    payload: {
        section: Position;
        content: string;
        reason?: string;     // 替换原因
    };
}

/**
 * 优化段落
 */
export interface OptimizeSectionFunction extends AIAssistantFunction {
    type: 'OPTIMIZE_SECTION';
    payload: {
        section: Position;
        suggestions: Array<{
            content: string;
            reason: string;    // 优化原因
        }>;
    };
}

/**
 * 生成大纲
 */
export interface GenerateOutlineFunction extends AIAssistantFunction {
    type: 'GENERATE_OUTLINE';
    payload: {
        outline: Array<{
            level: number;     // 大纲层级
            title: string;     // 标题
            description?: string; // 描述
        }>;
    };
}

/**
 * 推荐标签
 */
export interface SuggestTagsFunction extends AIAssistantFunction {
    type: 'SUGGEST_TAGS';
    payload: {
        tags: Array<{
            name: string;
            confidence: number; // 置信度
            category?: string;  // 标签分类
        }>;
    };
}

/**
 * 润色文章
 */
export interface PolishWritingFunction extends AIAssistantFunction {
    type: 'POLISH_WRITING';
    payload: {
        improvements: Array<{
            original: string;
            suggested: string;
            reason: string;
            position: Position;
        }>;
    };
}

/**
 * 语法检查
 */
export interface CheckGrammarFunction extends AIAssistantFunction {
    type: 'CHECK_GRAMMAR';
    payload: {
        issues: Array<{
            type: 'grammar' | 'spelling' | 'style';
            text: string;
            suggestion: string;
            position: Position;
        }>;
    };
}

/**
 * 翻译段落
 */
export interface TranslateSectionFunction extends AIAssistantFunction {
    type: 'TRANSLATE_SECTION';
    payload: {
        section: Position;
        translation: string;
        targetLanguage: string;
        sourceLanguage?: string;
    };
}

/**
 * AI 助手函数联合类型
 */
export type AIFunction =
    | SetTitleFunction
    | SetContentFunction
    | UpdateContentFunction
    | SetSummaryFunction
    | SetTagsFunction
    | SetCoverFunction
    | ReplaceSectionFunction
    | OptimizeSectionFunction
    | GenerateOutlineFunction
    | SuggestTagsFunction
    | PolishWritingFunction
    | CheckGrammarFunction
    | TranslateSectionFunction;

export interface ActionButton {
    id: string;
    label: string;
    text?: string;
    description: string;
    metadata?: {
        stage?: WritingStage;
        priority?: number;
        requiresConfirmation?: boolean;
        [key: string]: any;
    };
}

export interface AISession {
    id: string;
    userId: string;
    stage: WritingStage;
    messages: Message[];
    context: {
        title?: string;
        keywords?: string[];
        outline?: string;
        content?: string;
        [key: string]: any;
    };
    createdAt: string;
    updatedAt: string;
    expiresAt: string;
}

export interface AIAnalysis {
    score: number;
    analysis: {
        metrics: {
            readabilityScore: number;
            keywordDensity: number;
            averageSentenceLength: number;
            [key: string]: number;
        };
        suggestions: Array<{
            type: string;
            description: string;
            priority: 'high' | 'medium' | 'low';
        }>;
    };
}

// AI 响应接口
export interface AIResponse {
    functions: AIFunction[];
    message?: string;      // AI 的解释或建议
    confidence?: number;   // AI 的整体确信度
    metadata?: {          // 额外元数据
        model: string;      // 使用的模型
        timestamp: number;  // 响应时间戳
        processingTime?: number; // 处理时间
    };
}
