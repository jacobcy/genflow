/**
 * 写作阶段
 * @description 定义文章写作的不同阶段
 */
export type WritingStage = 'topic' | 'writing' | 'optimization' | 'review';

/**
 * 消息类型
 * @description 定义系统中的消息格式，包括用户消息和AI助手消息
 */
export interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    type: 'text' | 'markdown' | 'html' | 'suggestion' | 'outline' | 'analysis';
    timestamp: string;
    metadata?: {
        stage?: WritingStage;
        confidence?: number;
        references?: string[];
        [key: string]: any;
    };
}

/**
 * 优先级类型
 * @description 定义系统中各种操作和建议的优先级
 */
export type Priority = 'high' | 'medium' | 'low';

/**
 * 文档格式类型
 * @description 定义系统支持的文档格式
 */
export type DocumentFormat = 'markdown' | 'html' | 'text';

/**
 * 位置信息
 * @description 定义文档中的位置信息
 */
export interface Position {
    start: number;
    end: number;
}

/**
 * 基础元数据
 * @description 定义基础的元数据结构
 */
export interface BaseMetadata {
    createdAt?: string;
    updatedAt?: string;
    version?: string;
    [key: string]: any;
}

/**
 * 操作结果
 * @description 定义操作的结果状态
 */
export interface OperationResult<T = any> {
    success: boolean;
    data?: T;
    error?: {
        code: string;
        message: string;
        details?: any;
    };
}

/**
 * WebSocket 消息
 * @description 定义 WebSocket 通信的消息格式
 */
export interface WebSocketMessage {
    type: string;
    payload: any;
    metadata: {
        timestamp: number;
        version?: string;
        sessionId?: string;
    };
}

/**
 * WebSocket 配置
 * @description 定义 WebSocket 连接的配置选项
 */
export interface WebSocketConfig {
    url: string;
    token: string;
    onMessage?: (message: WebSocketMessage) => void;
    onError?: (error: Event) => void;
    onClose?: () => void;
} 