'use client';

import { ReactNode, useState } from 'react';
import Sidebar from './Sidebar';
import { Header } from '@/components/layout/Header';

interface UserLayoutProps {
  children: ReactNode;
}

export default function UserLayout({ children }: UserLayoutProps) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  // 处理侧边栏折叠状态变化
  const handleSidebarCollapse = (collapsed: boolean) => {
    setIsSidebarCollapsed(collapsed);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 via-gray-50/90 to-white dark:from-gray-900 dark:via-gray-900/95 dark:to-gray-800/90">
      <Header />
      <Sidebar onCollapse={handleSidebarCollapse} />
      <div
        className={`transition-[padding] duration-300 ${isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'}`}
      >
        <main
          style={{
            paddingTop: 'calc(4rem + 1px)',
            transition: 'padding-top 0.3s ease-in-out'
          }}
          className="relative min-h-[calc(100vh-4rem)]"
        >
          <div className="mx-auto max-w-7xl px-4 pb-12 sm:px-6 lg:px-8 min-h-full flex flex-col">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
