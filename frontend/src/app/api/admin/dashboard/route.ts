import { NextRequest, NextResponse } from 'next/server';

// 模拟仪表盘数据
export async function GET(request: NextRequest) {
  try {
    // 检查认证（这里应该从请求中获取令牌并验证）
    // 实际环境中应使用正确的认证中间件

    // 模拟统计数据
    const stats = {
      total_users: 10,
      total_articles: 250,
      today_visits: 87,
      system_status: '正常'
    };

    // 模拟访问趋势数据
    const visits = {
      labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      data: [65, 59, 80, 81, 56, 55, 40]
    };

    // 模拟用户增长数据
    const users = {
      labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
      data: [5, 10, 15, 20, 25, 30]
    };

    // 获取最新用户数据
    const latestUsers = [
      {
        id: '1',
        username: '管理员',
        email: 'admin@example.com',
        avatar_url: 'https://ui-avatars.com/api/?name=Admin&background=0D8ABC&color=fff',
        is_active: true,
        created_at: '2023-01-01T00:00:00Z'
      },
      {
        id: '2',
        username: '测试用户',
        email: 'user@example.com',
        avatar_url: 'https://ui-avatars.com/api/?name=User&background=0DBC8A&color=fff',
        is_active: true,
        created_at: '2023-01-02T00:00:00Z'
      },
      {
        id: '3',
        username: '用户3',
        email: 'user3@example.com',
        avatar_url: 'https://ui-avatars.com/api/?name=User3&background=0DBC8A&color=fff',
        is_active: true,
        created_at: '2023-01-03T00:00:00Z'
      },
      {
        id: '4',
        username: '用户4',
        email: 'user4@example.com',
        avatar_url: 'https://ui-avatars.com/api/?name=User4&background=0DBC8A&color=fff',
        is_active: false,
        created_at: '2023-01-04T00:00:00Z'
      },
      {
        id: '5',
        username: '用户5',
        email: 'user5@example.com',
        avatar_url: 'https://ui-avatars.com/api/?name=User5&background=0DBC8A&color=fff',
        is_active: true,
        created_at: '2023-01-05T00:00:00Z'
      }
    ];

    return NextResponse.json({
      stats,
      visits,
      users,
      latest_users: latestUsers
    });
  } catch (error) {
    console.error('Error getting dashboard data:', error);
    return NextResponse.json(
      { error: 'Failed to get dashboard data' },
      { status: 500 }
    );
  }
}
