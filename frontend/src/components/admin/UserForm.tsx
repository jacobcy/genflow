'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id?: string;
  email: string;
  username: string;
  role: 'admin' | 'user';
  is_active: boolean;
}

interface UserFormProps {
  userId?: string;
  isNew?: boolean;
}

export default function UserForm({ userId, isNew = false }: UserFormProps) {
  const [user, setUser] = useState<User>({
    email: '',
    username: '',
    role: 'user',
    is_active: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const router = useRouter();

  // 如果不是新用户，加载现有用户数据
  useEffect(() => {
    if (!isNew && userId) {
      const fetchUser = async () => {
        try {
          setLoading(true);
          const response = await fetch(`/api/admin/users/${userId}`);
          
          if (!response.ok) {
            throw new Error('Failed to fetch user');
          }
          
          const userData = await response.json();
          setUser(userData);
          setError(null);
        } catch (err) {
          setError('获取用户数据失败');
          console.error(err);
        } finally {
          setLoading(false);
        }
      };
      
      fetchUser();
    }
  }, [isNew, userId]);

  // 表单输入处理
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setUser(prev => ({ ...prev, [name]: checked }));
    } else {
      setUser(prev => ({ ...prev, [name]: value }));
    }
  };

  // 表单提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      let response;
      
      if (isNew) {
        // 创建新用户
        response = await fetch('/api/admin/users', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(user),
        });
      } else {
        // 更新现有用户
        response = await fetch(`/api/admin/users/${userId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(user),
        });
      }
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save user');
      }
      
      const savedUser = await response.json();
      
      setSuccess(isNew ? '用户创建成功！' : '用户更新成功！');
      
      // 如果是新用户，2秒后重定向
      if (isNew) {
        setTimeout(() => {
          router.push('/admin/dashboard');
        }, 2000);
      }
    } catch (err) {
      console.error(err);
      setError(`${isNew ? '创建' : '更新'}用户失败：${err}`);
    } finally {
      setLoading(false);
    }
  };

  // 返回仪表盘
  const handleCancel = () => {
    router.push('/admin/dashboard');
  };

  if (loading && !isNew) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">加载中...</span>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 w-full">
      <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-200 mb-6">
        {isNew ? '创建新用户' : '编辑用户'}
      </h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
          <span className="block sm:inline">{success}</span>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2" htmlFor="email">
            邮箱地址
          </label>
          <input
            id="email"
            name="email"
            type="email"
            value={user.email}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2" htmlFor="username">
            用户名
          </label>
          <input
            id="username"
            name="username"
            type="text"
            value={user.username}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2" htmlFor="role">
            角色
          </label>
          <select
            id="role"
            name="role"
            value={user.role}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          >
            <option value="user">用户</option>
            <option value="admin">管理员</option>
          </select>
        </div>
        
        <div className="mb-6">
          <div className="flex items-center">
            <input
              id="is_active"
              name="is_active"
              type="checkbox"
              checked={user.is_active}
              onChange={handleChange}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-700 dark:text-gray-300" htmlFor="is_active">
              账户激活
            </label>
          </div>
        </div>
        
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={handleCancel}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
          >
            取消
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {loading ? '保存中...' : '保存'}
          </button>
        </div>
      </form>
    </div>
  );
}