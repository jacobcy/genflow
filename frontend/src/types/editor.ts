import { Position, BaseMetadata } from './common';

/**
 * 编辑器模式
 * @description 定义编辑器的不同工作模式
 */
export type EditorMode = 'edit' | 'preview' | 'split';

/**
 * 编辑器操作类型
 * @description 定义编辑器支持的操作类型
 */
export type EditorOperationType = 'insert' | 'delete' | 'replace' | 'format';

/**
 * 格式化类型
 * @description 定义文本格式化的类型
 */
export interface FormatOptions {
    bold?: boolean;
    italic?: boolean;
    underline?: boolean;
    strikethrough?: boolean;
    heading?: number | null;
    link?: string;
    color?: string;
    backgroundColor?: string;
    fontSize?: number;
    fontFamily?: string;
    alignment?: 'left' | 'center' | 'right' | 'justify';
    lineHeight?: number;
    [key: string]: any;
}

/**
 * 编辑器操作
 * @description 定义编辑器的基本操作
 */
export interface EditorOperation {
    type: EditorOperationType;
    position: Position;
    content?: string;
    format?: FormatOptions;
    timestamp: number;
    metadata?: {
        source?: 'user' | 'ai' | 'system';
        reason?: string;
        [key: string]: any;
    };
}

/**
 * 编辑器历史记录
 * @description 定义编辑器的撤销/重做历史
 */
export interface EditorHistory {
    undo: Array<EditorOperation>;
    redo: Array<EditorOperation>;
    maxSize?: number;
}

/**
 * 自动完成项
 * @description 定义编辑器的自动完成建议
 */
export interface CompletionItem {
    id: string;
    content: string;
    position: Position;
    type?: 'text' | 'snippet' | 'command';
    metadata?: {
        description?: string;
        documentation?: string;
        source?: 'user' | 'ai' | 'system';
        [key: string]: any;
    };
}

/**
 * 编辑器状态
 * @description 定义编辑器的完整状态
 */
export interface EditorState {
    sessionId: string;
    version: string;
    isDirty: boolean;
    mode: EditorMode;
    history: EditorHistory;
    format: FormatOptions;
    completions: Array<CompletionItem>;
    viewport: {
        scrollTop: number;
        scrollLeft: number;
        width: number;
        height: number;
    };
    selection?: {
        ranges: Array<Position>;
        focus: Position;
        anchor: Position;
    };
}

/**
 * 编辑器配置
 * @description 定义编辑器的配置选项
 */
export interface EditorConfig {
    theme: 'light' | 'dark';
    fontSize: number;
    fontFamily: string;
    lineHeight: number;
    tabSize: number;
    useSoftTabs: boolean;
    showLineNumbers: boolean;
    wordWrap: boolean;
    autoSave: boolean;
    autoSaveInterval: number;
    maxHistorySize: number;
    plugins?: Array<{
        name: string;
        enabled: boolean;
        config?: any;
    }>;
}

/**
 * 编辑器插件
 * @description 定义编辑器插件的接口
 */
export interface EditorPlugin {
    name: string;
    version: string;
    description?: string;
    initialize: (editor: any) => void;
    destroy: () => void;
    handlers: {
        [key: string]: (...args: any[]) => void;
    };
}
