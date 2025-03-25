'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthContext';
import UserLayout from '@/components/user/Layout';
import ArticleEditor from '@/components/user/articles/ArticleEditor';
import { getArticle } from '@/lib/api/articles';
import { use } from 'react';
import AISidebar from '@/components/ai/AISidebar';

interface Article {
  id: string;
  title: string;
  content: string;
  summary: string;
  tags: string[];
  cover_image?: string;
  coverImage?: string;
  status: 'draft' | 'published';
  author: {
    id: string;
  };
}

export default function EditArticlePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { isAuthenticated, user, loading } = useAuth();
  const router = useRouter();
  const [article, setArticle] = useState<Article | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const [showAIAssistant, setShowAIAssistant] = useState(true);

  // 加载文章数据
  useEffect(() => {
    console.log("编辑页面：加载文章数据useEffect执行", { isAuthenticated, loading, id, user });

    if (id) {
      setIsLoading(true);
      getArticle(id)
        .then((data) => {
          console.log("编辑页面：文章数据获取成功", data);
          // 在开发环境中，可以选择放宽此条件
          if (process.env.NODE_ENV !== 'development' && data.author.id !== user?.id) {
            setError('您没有权限编辑此文章');
            setIsLoading(false);
            return;
          }
          setArticle(data);
          setIsLoading(false);
        })
        .catch((err) => {
          console.error("编辑页面：文章获取失败", err);
          setError('加载文章失败: ' + err.message);
          setIsLoading(false);
        });
    }
  }, [id, user]);

  // 未登录显示明确的未登录提示，而不是空白页或无限加载
  if (!loading && !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center p-6 max-w-md bg-white rounded-lg border border-gray-200 shadow-md dark:bg-gray-800 dark:border-gray-700">
          <h2 className="mb-2 text-2xl font-bold text-gray-900 dark:text-white">需要登录</h2>
          <p className="mb-5 text-gray-700 dark:text-gray-400">您需要登录才能编辑文章</p>
          <div className="flex space-x-4 justify-center">
            <button
              onClick={() => router.push('/login')}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 focus:ring-4 focus:outline-none focus:ring-primary-300 dark:bg-primary-600 dark:hover:bg-primary-700 dark:focus:ring-primary-800"
            >
              前往登录
            </button>
            {process.env.NODE_ENV === 'development' && (
              <button
                onClick={() => {
                  // @ts-ignore - 开发环境全局变量
                  if (window.__GENFLOW_AUTH_TOOLS?.mockLogin) {
                    // @ts-ignore
                    window.__GENFLOW_AUTH_TOOLS.mockLogin('user');
                  } else {
                    alert('开发工具未初始化，请刷新页面后重试');
                  }
                }}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-200 rounded-lg hover:bg-gray-100 hover:text-primary-600 focus:z-10 focus:ring-4 focus:outline-none focus:ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
              >
                开发模式登录
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // 如果是管理员，提示应该去管理员界面
  if (!loading && isAuthenticated && user?.role !== 'user') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center p-6 max-w-md bg-white rounded-lg border border-gray-200 shadow-md dark:bg-gray-800 dark:border-gray-700">
          <h2 className="mb-2 text-2xl font-bold text-gray-900 dark:text-white">访问受限</h2>
          <p className="mb-5 text-gray-700 dark:text-gray-400">管理员账号应该访问管理员界面</p>
          <button
            onClick={() => router.push('/admin/dashboard')}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 focus:ring-4 focus:outline-none focus:ring-primary-300 dark:bg-primary-600 dark:hover:bg-primary-700 dark:focus:ring-primary-800"
          >
            前往管理界面
          </button>
        </div>
      </div>
    );
  }

  if (loading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">加载中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <UserLayout>
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">错误!</strong>
          <span className="block sm:inline"> {error}</span>
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-3">
              <button
                onClick={() => window.location.reload()}
                className="mr-2 inline-flex items-center px-4 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-200 rounded-lg hover:bg-gray-100 hover:text-primary-600 focus:z-10 focus:ring-4 focus:outline-none focus:ring-gray-200"
              >
                刷新页面
              </button>
              <button
                onClick={() => router.push(`/user/articles/${id}`)}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-200 rounded-lg hover:bg-gray-100 hover:text-primary-600 focus:z-10 focus:ring-4 focus:outline-none focus:ring-gray-200"
              >
                返回查看
              </button>
            </div>
          )}
        </div>
      </UserLayout>
    );
  }

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
                  编辑文章
                </h1>
              </div>
              {article && (
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
              )}
            </div>
            <div className="pb-6">
              {article && <ArticleEditor article={article} />}
            </div>
          </div>
        </div>

        {/* AI助手侧边栏 */}
        {user && (
          <AISidebar
            userId={user.id}
            articleId={id}
            showByDefault={showAIAssistant}
          />
        )}
      </div>
    </UserLayout>
  );
}