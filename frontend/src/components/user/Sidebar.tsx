'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthContext';

interface SidebarProps {
  onCollapse?: (collapsed: boolean) => void;
}

interface SidebarItem {
  name: string;
  href: string;
  icon: React.ReactNode;
}

// 侧边栏图标组件
const DashboardIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
  </svg>
);

const ArticlesIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
  </svg>
);

const DraftsIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
  </svg>
);

const PublishedIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const NewArticleIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
  </svg>
);

const ProfileIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
);

const AIToolsIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
  </svg>
);

// 创作工具图标
const HotlistIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
  </svg>
);

const AIAssistantIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
  </svg>
);

const MDEditorIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
  </svg>
);

export default function Sidebar({ onCollapse }: SidebarProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const pathname = usePathname();
  const { user } = useAuth();

  // 侧边栏导航项
  const navigation: SidebarItem[] = [
    { name: '全部文章', href: '/user/articles', icon: <ArticlesIcon /> },
    { name: '草稿箱', href: '/user/articles/drafts', icon: <DraftsIcon /> },
    { name: '已发布', href: '/user/articles/published', icon: <PublishedIcon /> },
    { name: '写文章', href: '/user/articles/new', icon: <NewArticleIcon /> },
    { name: '个人信息', href: '/user/profile', icon: <ProfileIcon /> },
    { name: '今日热榜', href: 'http://localhost:6699', icon: <HotlistIcon /> },
    { name: 'AI 助手', href: '/test/ai', icon: <AIAssistantIcon /> },
    { name: 'MD 编辑器', href: 'http://localhost:9000', icon: <MDEditorIcon /> },
  ];

  // 判断当前路径是否激活
  const isActive = (path: string) => {
    if (path === '/user/dashboard') {
      return pathname === path;
    }
    // 对于全部文章页面，使用精确匹配
    if (path === '/user/articles') {
      return pathname === path;
    }
    // 其他页面使用前缀匹配
    return pathname.startsWith(path);
  };

  // 切换折叠状态
  const toggleCollapse = () => {
    const newCollapsed = !isCollapsed;
    setIsCollapsed(newCollapsed);
    onCollapse?.(newCollapsed);
  };

  return (
    <>
      {/* 移动端菜单按钮 */}
      <button
        type="button"
        className="lg:hidden fixed z-50 bottom-4 right-4 p-2 rounded-full bg-primary-600 text-white shadow-lg"
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
      >
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d={isMobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"}
          />
        </svg>
      </button>

      {/* 移动端侧边栏 */}
      <div
        className={`fixed inset-0 z-40 lg:hidden ${isMobileMenuOpen ? "block" : "hidden"
          }`}
      >
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setIsMobileMenuOpen(false)} />
        <nav className="fixed top-0 left-0 bottom-0 flex flex-col w-72 max-w-xs bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700/50">
          <div className="flex-1 overflow-y-auto py-6 px-4">
            {/* 导航项 */}
            <div className="space-y-1">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${isActive(item.href)
                    ? "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white"
                    : "text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800/50"
                    }`}
                >
                  {item.icon}
                  <span className="ml-3">{item.name}</span>
                </Link>
              ))}
            </div>
          </div>
        </nav>
      </div>

      {/* 桌面端侧边栏 */}
      <div className={`hidden lg:fixed lg:inset-y-0 lg:flex lg:flex-col transition-[width] duration-300 ease-in-out ${isCollapsed ? 'lg:w-20' : 'lg:w-64'}`}>
        <div className="flex-1 flex flex-col min-h-0 bg-gradient-to-r from-gray-50/95 to-white/80 dark:from-gray-900 dark:to-gray-800/90 backdrop-blur-sm border-r border-gray-200/60 dark:border-gray-700/40 relative">
          {/* 折叠按钮 */}
          <button
            type="button"
            onClick={toggleCollapse}
            className="absolute top-1/2 -translate-y-1/2 right-0 -mr-3 h-8 w-8 rounded-full bg-white/90 dark:bg-gray-800 border border-gray-200/60 dark:border-gray-700/40 flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-750 focus:outline-none focus:ring-2 focus:ring-primary-500/50 dark:focus:ring-offset-gray-900 z-50 backdrop-blur-sm"
          >
            <svg
              className={`h-5 w-5 transform transition-transform duration-300 ease-in-out ${isCollapsed ? 'rotate-180' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
          </button>

          <div className="flex-1 flex flex-col pt-24 pb-4 overflow-y-auto">
            {/* 导航项 */}
            <nav className="flex-1 px-3 space-y-1">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-all duration-300 ease-in-out ${isActive(item.href)
                    ? "bg-white/60 dark:bg-gray-800/60 text-gray-900 dark:text-white shadow-sm backdrop-blur-sm"
                    : "text-gray-600 hover:bg-white/40 dark:text-gray-300 dark:hover:bg-gray-800/40"
                    }`}
                >
                  {item.icon}
                  <span className={`ml-3 transition-all duration-300 ease-in-out ${isCollapsed ? 'opacity-0 w-0 -ml-3' : 'opacity-100 w-auto'}`}>
                    {item.name}
                  </span>
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </div>
    </>
  );
}
