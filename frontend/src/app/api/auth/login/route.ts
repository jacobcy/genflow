import { NextRequest, NextResponse } from 'next/server';
import { User, UserRole } from '@/lib/auth/authUtils';

// 模拟用户数据库
const users = [
  {
    id: '1',
    email: 'user@example.com',
    password: 'user123', // 与前端模拟登录使用的密码一致
    role: 'user',
    name: '普通用户'
  },
  {
    id: '2',
    email: 'admin@example.com',
    password: 'admin123',
    role: 'admin',
    name: '管理员'
  }
];

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { email, password } = body;

    // 简单的验证
    if (!email || !password) {
      return NextResponse.json(
        { message: '邮箱和密码不能为空' },
        { status: 400 }
      );
    }

    // 查找用户
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());

    // 如果用户不存在或密码不匹配
    if (!user || user.password !== password) {
      return NextResponse.json(
        { message: '邮箱或密码不正确' },
        { status: 401 }
      );
    }

    // 创建安全的用户对象（不包含密码）
    const secureUser = {
      id: user.id,
      email: user.email,
      role: user.role,
      name: user.name
    };

    // 生成模拟token
    const token = `token_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // 确定重定向路径
    const redirect = user.role === 'admin' ? '/admin/dashboard' : '/user/dashboard';

    // 返回成功响应
    return NextResponse.json({
      access_token: token,
      user: secureUser,
      redirect
    });
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { message: '登录过程中发生错误' },
      { status: 500 }
    );
  }
}
