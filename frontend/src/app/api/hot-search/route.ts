import { NextResponse } from 'next/server';

export async function GET() {
    try {
        const response = await fetch('https://zj.v.api.aa1.cn/api/weibo-rs/', {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        });

        const data = await response.json();

        return NextResponse.json({ data });
    } catch (error) {
        console.error('获取抖音热搜失败:', error);
        return NextResponse.json({ error: '获取热搜数据失败' }, { status: 500 });
    }
}
