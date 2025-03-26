import { NextRequest, NextResponse } from 'next/server';
import { User, UserRole } from '@/lib/auth/authUtils';

// 模拟用户数据（与用户列表API保持同步）
let users = [
  {
    id: '1',
    email: 'admin@example.com',
    username: '管理员',
    role: 'admin',
    avatar_url: 'https://ui-avatars.com/api/?name=Admin&background=0D8ABC&color=fff',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z'
  },
  {
    id: '2',
    email: 'user@example.com',
    username: '测试用户',
    role: 'user',
    avatar_url: 'https://ui-avatars.com/api/?name=User&background=0DBC8A&color=fff',
    is_active: true,
    created_at: '2023-01-02T00:00:00Z'
  }
];

for (let i = 3; i <= 10; i++) {
  users.push({
    id: i.toString(),
    email: `user${i}@example.com`,
    username: `用户${i}`,
    role: 'user',
    avatar_url: `https://ui-avatars.com/api/?name=User${i}&background=0DBC8A&color=fff`,
    is_active: Math.random() > 0.3,
    created_at: new Date(Date.now() - Math.floor(Math.random() * 10000000000)).toISOString()
  });
}

// 获取单个用户
export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const { id } = params;

    // 模拟用户数据
    const mockUser: User = {
      id,
      name: '测试用户',
      email: 'test@example.com',
      role: 'user' as const,
      avatar: '/images/default_avatar.jpg'
    };

    return NextResponse.json(mockUser);

  } catch (error) {
    console.error('Get User Error:', error);
    return NextResponse.json(
      { error: '获取用户信息失败' },
      { status: 500 }
    );
  }
}

// 更新用户
export async function PUT(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const { id } = params;
    const body = await req.json();
    const { name, email } = body;

    // 验证必填字段
    if (!name || !email) {
      return NextResponse.json(
        { error: '缺少必填字段' },
        { status: 400 }
      );
    }

    // 模拟更新用户
    const updatedUser: User = {
      id,
      name,
      email,
      role: 'user' as const,
      avatar: '/images/default_avatar.jpg'
    };

    return NextResponse.json(updatedUser);

  } catch (error) {
    console.error('Update User Error:', error);
    return NextResponse.json(
      { error: '更新用户信息失败' },
      { status: 500 }
    );
  }
}

// 删除用户
export async function DELETE(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const { id } = params;

    // 模拟删除用户
    return NextResponse.json({ success: true });

  } catch (error) {
    console.error('Delete User Error:', error);
    return NextResponse.json(
      { error: '删除用户失败' },
      { status: 500 }
    );
  }
}
