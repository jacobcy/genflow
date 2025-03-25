import { NextRequest, NextResponse } from 'next/server';

// 模拟用户数据
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

// 获取所有用户
export async function GET(request: NextRequest) {
  try {
    // 检查认证（这里应该从请求中获取令牌并验证）
    // 实际环境中应使用正确的认证中间件

    // 处理分页
    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '10');

    const start = (page - 1) * limit;
    const end = start + limit;

    const paginatedUsers = users.slice(start, end);

    return NextResponse.json({
      users: paginatedUsers,
      total: users.length,
      page,
      limit
    });
  } catch (error) {
    console.error('Error getting users:', error);
    return NextResponse.json(
      { error: 'Failed to get users' },
      { status: 500 }
    );
  }
}

// 创建新用户
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // 验证必要字段
    if (!body.email || !body.username || !body.role) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // 检查邮箱是否已存在
    if (users.some(user => user.email === body.email)) {
      return NextResponse.json(
        { error: 'Email already exists' },
        { status: 409 }
      );
    }

    // 创建新用户
    const newUser = {
      id: (users.length + 1).toString(),
      email: body.email,
      username: body.username,
      role: body.role,
      avatar_url: `https://ui-avatars.com/api/?name=${encodeURIComponent(body.username)}&background=0DBC8A&color=fff`,
      is_active: true,
      created_at: new Date().toISOString()
    };

    users.push(newUser);

    return NextResponse.json(newUser, { status: 201 });
  } catch (error) {
    console.error('Error creating user:', error);
    return NextResponse.json(
      { error: 'Failed to create user' },
      { status: 500 }
    );
  }
}