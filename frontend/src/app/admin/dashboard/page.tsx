'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthContext';
import StatCard from '@/components/admin/StatCard';
import DashboardChart from '@/components/admin/DashboardChart';
import UserList from '@/components/admin/UserList';

// 图标组件
const UsersIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd"></path>
  </svg>
);

const ArticlesIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd"></path>
  </svg>
);

const VisitsIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"></path>
    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd"></path>
  </svg>
);

const ServerIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path fillRule="evenodd" d="M2 5a2 2 0 012-2h12a2 2 0 012 2v2a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm14 1a1 1 0 11-2 0 1 1 0 012 0zM2 13a2 2 0 012-2h12a2 2 0 012 2v2a2 2 0 01-2 2H4a2 2 0 01-2-2v-2zm14 1a1 1 0 11-2 0 1 1 0 012 0z" clipRule="evenodd"></path>
  </svg>
);

interface DashboardData {
  stats: {
    total_users: number;
    total_articles: number;
    today_visits: number;
    system_status: string;
  };
  visits: {
    labels: string[];
    data: number[];
  };
  users: {
    labels: string[];
    data: number[];
  };
  latest_users: any[];
}

export default function AdminDashboard() {
  const { isAuthenticated, user, loading } = useAuth();
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [dataLoading, setDataLoading] = useState(true);

  // 身份验证检查
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    } else if (!loading && isAuthenticated && user?.role !== 'admin') {
      router.push('/user/dashboard');
    }
  }, [isAuthenticated, user, loading, router]);

  // 加载仪表盘数据
  useEffect(() => {
    if (isAuthenticated && user?.role === 'admin') {
      const fetchDashboardData = async () => {
        try {
          setDataLoading(true);
          const response = await fetch('/api/admin/dashboard');

          if (!response.ok) {
            throw new Error('Failed to fetch dashboard data');
          }

          const data = await response.json();
          setDashboardData(data);
        } catch (error) {
          console.error('Error fetching dashboard data:', error);
        } finally {
          setDataLoading(false);
        }
      };

      fetchDashboardData();
    }
  }, [isAuthenticated, user]);

  if (loading || dataLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">加载中...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || user?.role !== 'admin' || !dashboardData) {
    return null;
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="container px-6 mx-auto py-24 sm:py-32">
        <h2 className="my-6 text-2xl font-semibold text-gray-700 dark:text-gray-200">
          仪表盘
        </h2>

        {/* 统计卡片 */}
        <div className="grid gap-6 mb-8 md:grid-cols-2 xl:grid-cols-4">
          <StatCard
            title="用户总数"
            value={dashboardData.stats.total_users}
            icon={<UsersIcon />}
            colorClass="text-orange-500 dark:text-orange-100"
            bgClass="bg-orange-100 dark:bg-orange-500"
          />
          <StatCard
            title="文章总数"
            value={dashboardData.stats.total_articles}
            icon={<ArticlesIcon />}
            colorClass="text-green-500 dark:text-green-100"
            bgClass="bg-green-100 dark:bg-green-500"
          />
          <StatCard
            title="今日访问"
            value={dashboardData.stats.today_visits}
            icon={<VisitsIcon />}
            colorClass="text-blue-500 dark:text-blue-100"
            bgClass="bg-blue-100 dark:bg-blue-500"
          />
          <StatCard
            title="系统状态"
            value={dashboardData.stats.system_status}
            icon={<ServerIcon />}
            colorClass="text-teal-500 dark:text-teal-100"
            bgClass="bg-teal-100 dark:bg-teal-500"
          />
        </div>

        {/* 图表 */}
        <div className="grid gap-6 mb-8 md:grid-cols-2">
          <DashboardChart
            title="访问趋势"
            chartData={dashboardData.visits}
            chartType="line"
            chartId="visitsChart"
            colorClass="rgb(59, 130, 246)"
          />
          <DashboardChart
            title="用户增长"
            chartData={dashboardData.users}
            chartType="bar"
            chartId="usersChart"
            colorClass="rgb(16, 185, 129)"
          />
        </div>

        {/* 用户列表 */}
        <UserList />
      </div>
    </div>
  );
}