import { NextResponse } from 'next/server';
import { headers } from 'next/headers';

export async function GET() {
  try {
    const headersList = headers();
    const authorization = headersList.get('Authorization');
    
    // 检查是否有认证令牌
    if (!authorization || !authorization.startsWith('Bearer ')) {
      return NextResponse.json({
        authenticated: false,
        user: null
      });
    }
    
    const token = authorization.split(' ')[1];
    
    // 在实际应用中，这里会验证token是否有效
    // 此处简化处理，仅检查token是否存在
    if (!token) {
      return NextResponse.json({
        authenticated: false,
        user: null
      });
    }
    
    // 模拟从token中提取用户信息
    // 在实际应用中，这里会根据token获取实际用户数据
    // 假设token中包含了角色信息
    const isAdmin = token.includes('admin');
    
    const mockUser = {
      id: isAdmin ? '2' : '1',
      email: isAdmin ? 'admin@example.com' : 'user@example.com',
      role: isAdmin ? 'admin' : 'user',
      name: isAdmin ? '管理员' : '普通用户'
    };
    
    return NextResponse.json({
      authenticated: true,
      user: mockUser
    });
  } catch (error) {
    console.error('Verify error:', error);
    return NextResponse.json(
      { 
        authenticated: false,
        message: '验证过程中发生错误' 
      },
      { status: 500 }
    );
  }
}