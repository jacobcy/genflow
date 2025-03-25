'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  avatar_url: string;
  is_active: boolean;
  created_at: string;
}

export default function UserList() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [limit, setLimit] = useState(10);
  const router = useRouter();

  // 加载用户数据
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/admin/users?page=${page}&limit=${limit}`);

        if (!response.ok) {
          throw new Error('Failed to fetch users');
        }

        const data = await response.json();
        setUsers(data.users);
        setTotal(data.total);
        setError(null);
      } catch (err) {
        setError('获取用户列表失败');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [page, limit]);

  // 删除用户
  const handleDeleteUser = async (userId: string) => {
    if (!confirm('确定要删除此用户吗？')) {
      return;
    }

    try {
      const response = await fetch(`/api/admin/users/${userId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete user');
      }

      // 重新加载用户列表
      setUsers(users.filter(user => user.id !== userId));
      setTotal(prev => prev - 1);
    } catch (err) {
      console.error(err);
      alert('删除用户失败：' + err);
    }
  };

  // 处理状态切换
  const handleToggleStatus = async (userId: string, isActive: boolean) => {
    try {
      const response = await fetch(`/api/admin/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: !isActive }),
      });

      if (!response.ok) {
        throw new Error('Failed to update user status');
      }

      const updatedUser = await response.json();

      // 更新本地用户列表
      setUsers(users.map(user =>
        user.id === userId ? { ...user, is_active: !isActive } : user
      ));
    } catch (err) {
      console.error(err);
      alert('更新用户状态失败');
    }
  };

  // 编辑用户
  const handleEditUser = (userId: string) => {
    router.push(`/admin/users/${userId}`);
  };

  // 添加用户
  const handleAddUser = () => {
    router.push('/admin/users/new');
  };

  // 格式化日期
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      // 检查日期是否有效
      if (isNaN(date.getTime())) {
        return '日期无效';
      }
      return new Intl.DateTimeFormat('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (error) {
      return '日期无效';
    }
  };

  // 处理分页
  const handlePrevPage = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };

  const handleNextPage = () => {
    if (page * limit < total) {
      setPage(page + 1);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">加载中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">错误：</strong>
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  return (
    <div className="w-full overflow-hidden rounded-lg shadow-xs">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-300">用户管理</h3>
        <button
          onClick={handleAddUser}
          className="px-4 py-2 text-sm font-medium leading-5 text-white transition-colors duration-150 bg-primary-600 border border-transparent rounded-md active:bg-primary-600 hover:bg-primary-700 focus:outline-none focus:shadow-outline-primary"
        >
          添加用户
        </button>
      </div>

      <div className="w-full overflow-x-auto">
        <table className="w-full whitespace-no-wrap">
          <thead>
            <tr className="text-xs font-semibold tracking-wide text-left text-gray-500 uppercase border-b dark:border-gray-700 bg-gray-50 dark:text-gray-400 dark:bg-gray-800">
              <th className="px-4 py-3">用户</th>
              <th className="px-4 py-3">角色</th>
              <th className="px-4 py-3">注册时间</th>
              <th className="px-4 py-3">状态</th>
              <th className="px-4 py-3">操作</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y dark:divide-gray-700 dark:bg-gray-800">
            {users.map(user => (
              <tr key={user.id} className="text-gray-700 dark:text-gray-400">
                <td className="px-4 py-3">
                  <div className="flex items-center text-sm">
                    <div className="relative hidden w-8 h-8 mr-3 rounded-full md:block">
                      <img
                        className="object-cover w-full h-full rounded-full"
                        src={user.avatar_url}
                        alt={user.username}
                        loading="lazy"
                      />
                      <div className="absolute inset-0 rounded-full shadow-inner" aria-hidden="true"></div>
                    </div>
                    <div>
                      <p className="font-semibold">{user.username}</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">{user.email}</p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm">
                  <span className={`px-2 py-1 font-semibold leading-tight rounded-full ${user.role === 'admin'
                      ? 'text-yellow-700 bg-yellow-100 dark:text-yellow-100 dark:bg-yellow-700'
                      : 'text-green-700 bg-green-100 dark:text-green-100 dark:bg-green-700'
                    }`}>
                    {user.role === 'admin' ? '管理员' : '用户'}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm">
                  {formatDate(user.created_at)}
                </td>
                <td className="px-4 py-3 text-xs">
                  <span
                    className={`px-2 py-1 font-semibold leading-tight rounded-full ${user.is_active
                        ? 'text-green-700 bg-green-100 dark:text-green-100 dark:bg-green-700'
                        : 'text-red-700 bg-red-100 dark:text-red-100 dark:bg-red-700'
                      }`}
                  >
                    {user.is_active ? '正常' : '禁用'}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm space-x-2">
                  <button
                    onClick={() => handleEditUser(user.id)}
                    className="px-3 py-1 text-sm font-medium leading-5 text-white transition-colors duration-150 bg-primary-600 border border-transparent rounded-md active:bg-primary-600 hover:bg-primary-700 focus:outline-none focus:shadow-outline-primary"
                  >
                    编辑
                  </button>
                  <button
                    onClick={() => handleToggleStatus(user.id, user.is_active)}
                    className={`px-3 py-1 text-sm font-medium leading-5 text-white transition-colors duration-150 border border-transparent rounded-md focus:outline-none ${user.is_active
                        ? 'bg-orange-500 hover:bg-orange-600 focus:shadow-outline-orange'
                        : 'bg-green-500 hover:bg-green-600 focus:shadow-outline-green'
                      }`}
                  >
                    {user.is_active ? '禁用' : '启用'}
                  </button>
                  <button
                    onClick={() => handleDeleteUser(user.id)}
                    className="px-3 py-1 text-sm font-medium leading-5 text-white transition-colors duration-150 bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:shadow-outline-red"
                  >
                    删除
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 分页控制 */}
      <div className="px-4 py-3 text-xs font-semibold tracking-wide text-gray-500 uppercase border-t dark:border-gray-700 bg-gray-50 dark:text-gray-400 dark:bg-gray-800">
        <div className="flex items-center justify-between">
          <span>
            第 {page} 页，共 {Math.ceil(total / limit)} 页
          </span>
          <div className="flex items-center">
            <button
              onClick={handlePrevPage}
              disabled={page === 1}
              className={`px-3 py-1 rounded-md focus:outline-none ${page === 1
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
            >
              上一页
            </button>
            <button
              onClick={handleNextPage}
              disabled={page * limit >= total}
              className={`ml-2 px-3 py-1 rounded-md focus:outline-none ${page * limit >= total
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}