'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthContext';
import UserLayout from '@/components/user/Layout';
import ArticleEditor from '@/components/user/articles/ArticleEditor';
import AISidebar from '@/components/ai/AISidebar';

export default function NewArticlePage() {
  const { isAuthenticated, user, loading } = useAuth();
  const router = useRouter();
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const [showAIAssistant, setShowAIAssistant] = useState(true);

  // 身份验证检查
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    } else if (!loading && isAuthenticated && user?.role !== 'user') {
      router.push('/admin/dashboard');
    }
  }, [isAuthenticated, user, loading, router]);

  const handlePreviewToggle = () => {
    const editorInstance = document.getElementById('article-editor');
    if (editorInstance) {
      const previewButton = editorInstance.querySelector('[data-action="toggle-preview"]');
      if (previewButton instanceof HTMLButtonElement) {
        previewButton.click();
        setIsPreviewMode(!isPreviewMode);
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin h-5 w-5 border-t border-gray-900 dark:border-gray-100 mx-auto"></div>
          <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">加载中...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || user?.role !== 'user') {
    return null;
  }

  return (
    <UserLayout>
      <div className="min-h-[calc(100vh-64px)]">
        {/* 主编辑区域 */}
        <div className={`transition-all duration-300 ease-in-out ${showAIAssistant ? 'lg:mr-[calc(40vw+0.5rem)]' : 'lg:mr-20'
          } mx-auto max-w-[calc(100vw-2rem)] lg:max-w-[calc(100vw-20rem)] xl:max-w-[calc(100vw-22rem)]`}>
          <div className="pt-6 px-4 lg:px-6">
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                  创建新文章
                </h1>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handlePreviewToggle}
                  className="inline-flex items-center px-4 py-2 text-sm font-medium border border-gray-200 dark:border-transparent rounded-md text-gray-900 dark:text-white bg-white dark:bg-primary-600 hover:bg-gray-50 dark:hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-900 transition-colors shadow-sm"
                >
                  {isPreviewMode ? '返回编辑' : '立即预览'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const editorInstance = document.getElementById('article-editor');
                    if (editorInstance) {
                      const saveButton = editorInstance.querySelector('[data-action="save-draft"]');
                      if (saveButton instanceof HTMLButtonElement) {
                        saveButton.click();
                      }
                    }
                  }}
                  className="inline-flex items-center px-4 py-2 text-sm font-medium border border-gray-200 dark:border-transparent rounded-md text-gray-900 dark:text-white bg-white dark:bg-primary-600 hover:bg-gray-50 dark:hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-900 transition-colors shadow-sm"
                >
                  保存草稿
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const editorInstance = document.getElementById('article-editor');
                    if (editorInstance) {
                      const publishButton = editorInstance.querySelector('[data-action="publish"]');
                      if (publishButton instanceof HTMLButtonElement) {
                        publishButton.click();
                      }
                    }
                  }}
                  className="inline-flex items-center px-4 py-2 text-sm font-medium border border-gray-200 dark:border-transparent rounded-md text-gray-900 dark:text-white bg-white dark:bg-primary-600 hover:bg-gray-50 dark:hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-900 transition-colors shadow-sm"
                >
                  发布文章
                </button>
              </div>
            </div>
            <div className="pb-6">
              <ArticleEditor />
            </div>
          </div>
        </div>

        {/* AI助手侧边栏 */}
        {user && (
          <AISidebar
            userId={user.id}
            articleId="new"
            showByDefault={showAIAssistant}
          />
        )}
      </div>
    </UserLayout>
  );
}