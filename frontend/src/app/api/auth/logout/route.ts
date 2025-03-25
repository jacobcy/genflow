import { NextResponse } from 'next/server';

export async function POST() {
  try {
    // 在实际应用中，这里可能需要执行token失效处理

    return NextResponse.json({
      success: true,
      message: '成功登出'
    });
  } catch (error) {
    console.error('Logout error:', error);
    return NextResponse.json(
      { message: '登出过程中发生错误' },
      { status: 500 }
    );
  }
}