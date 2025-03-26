import { NextRequest, NextResponse } from 'next/server';
import { OpenAIService } from '@/lib/ai/openai-service';
import { SessionService } from '@/lib/ai/session-service';
import { Message } from '@/types/common';
import { ActionButton } from '@/types/ai-assistant';

const openAIService = new OpenAIService();
const sessionService = SessionService.getInstance();

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const { sessionId, actionId, userId, metadata } = body;

        if (!sessionId) {
            return NextResponse.json(
                { error: '缺少会话ID' },
                { status: 400 }
            );
        }

        const session = sessionService.getSession(sessionId);
        if (!session) {
            return NextResponse.json(
                { error: '会话不存在' },
                { status: 404 }
            );
        }

        // 根据动作类型执行相应的操作
        let result: { reply: Message; actions: ActionButton[] };
        switch (actionId) {
            case 'generate_outline': {
                const message: Message = {
                    id: Date.now().toString(),
                    role: 'user' as const,
                    content: '请根据当前主题生成一个详细的文章大纲。',
                    type: 'text',
                    timestamp: new Date().toISOString()
                };
                result = await openAIService.processMessage(
                    session.id,
                    message,
                    {
                        ...session.context,
                        stage: 'writing'
                    }
                );
                break;
            }

            case 'optimize_content': {
                const message: Message = {
                    id: Date.now().toString(),
                    role: 'user' as const,
                    content: '请分析当前内容并提供优化建议。',
                    type: 'text',
                    timestamp: new Date().toISOString()
                };
                result = await openAIService.processMessage(
                    session.id,
                    message,
                    {
                        ...session.context,
                        stage: 'optimization'
                    }
                );
                break;
            }

            case 'analyze_seo':
                if (session.context.content) {
                    const analysis = await openAIService.analyzeContent(session.context.content, 'seo');
                    const reply: Message = {
                        id: Date.now().toString(),
                        role: 'assistant' as const,
                        content: `SEO分析结果：\n\n${JSON.stringify(analysis, null, 2)}`,
                        type: 'markdown',
                        timestamp: new Date().toISOString()
                    };
                    result = {
                        reply,
                        actions: []
                    };
                } else {
                    return NextResponse.json(
                        { error: '没有可分析的内容' },
                        { status: 400 }
                    );
                }
                break;

            case 'final_check': {
                const message: Message = {
                    id: Date.now().toString(),
                    role: 'user' as const,
                    content: '请对文章进行最终审核，检查内容完整性、连贯性和错别字。',
                    type: 'text',
                    timestamp: new Date().toISOString()
                };
                result = await openAIService.processMessage(
                    session.id,
                    message,
                    {
                        ...session.context,
                        stage: 'review'
                    }
                );
                break;
            }

            default:
                return NextResponse.json(
                    { error: '未知的动作类型' },
                    { status: 400 }
                );
        }

        // 更新会话状态
        if (result.reply) {
            sessionService.addMessage(session.id, result.reply);
        }

        return NextResponse.json({
            message: result.reply,
            actions: result.actions
        });

    } catch (error) {
        console.error('AI Action API Error:', error);
        return NextResponse.json(
            { error: '处理请求时发生错误' },
            { status: 500 }
        );
    }
}
