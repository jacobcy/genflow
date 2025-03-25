import { NextRequest, NextResponse } from 'next/server';
import { OpenAIService } from '@/lib/ai/openai-service';
import { SessionService } from '@/lib/ai/session-service';
import { Message } from '@/types/common';

const openAIService = new OpenAIService();
const sessionService = SessionService.getInstance();

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const { sessionId, userId, message } = body;

        if (!userId) {
            return NextResponse.json(
                { error: '缺少用户ID' },
                { status: 400 }
            );
        }

        if (!message) {
            return NextResponse.json(
                { error: '消息内容不能为空' },
                { status: 400 }
            );
        }

        // 获取或创建会话
        let session = sessionId ? sessionService.getSession(sessionId) : null;
        if (!session) {
            session = sessionService.createSession(userId);
        }

        // 创建消息对象
        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user' as const,
            content: message,
            type: 'text',
            timestamp: new Date().toISOString()
        };

        // 添加消息到会话
        sessionService.addMessage(session.id, userMessage);

        // 处理消息
        const result = await openAIService.processMessage(
            session.id,
            userMessage,
            session.context
        );

        // 添加 AI 回复到会话
        if (result.reply) {
            sessionService.addMessage(session.id, result.reply);
        }

        // 返回响应
        return NextResponse.json({
            sessionId: session.id,
            reply: result.reply,
            actions: result.actions
        });

    } catch (error: any) {
        console.error('AI API Error:', error);

        // 返回用户友好的错误消息
        const errorMessage = error.message || 'AI 服务暂时不可用，请稍后重试';
        return NextResponse.json(
            { error: errorMessage },
            { status: error.status || 500 }
        );
    }
}

export async function GET(req: NextRequest) {
    const searchParams = req.nextUrl.searchParams;
    const sessionId = searchParams.get('sessionId');

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

    return NextResponse.json(session);
} 