'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  const router = useRouter();
  
  useEffect(() => {
    // 记录错误到错误报告服务
    console.error('页面错误:', error);
  }, [error]);
  
  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-white dark:bg-gray-900 px-4 py-16 sm:px-6 sm:py-24 md:grid md:place-items-center lg:px-8">
      <div className="max-w-max mx-auto">
        <main className="sm:flex">
          <div className="relative sm:mr-10">
            <div className="absolute inset-0 bg-gradient-to-r from-red-400 to-red-600 shadow-lg transform skew-y-0 -rotate-6 rounded-3xl opacity-50 sm:opacity-80"></div>
            <p className="relative text-8xl font-extrabold text-white tracking-wide sm:text-9xl py-8 px-10">
              500
            </p>
          </div>
          
          <div className="mt-6 sm:mt-0 sm:ml-6 flex flex-col justify-center">
            <div>
              <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight sm:text-4xl">
                服务器错误
              </h1>
              <p className="mt-3 text-base text-gray-500 dark:text-gray-400 max-w-md">
                抱歉，服务器在处理您的请求时出现了问题。我们的技术团队已经收到错误报告，正在紧急处理中。
              </p>
              {error.digest && (
                <p className="mt-2 text-sm font-mono text-gray-500 dark:text-gray-400">
                  错误ID: {error.digest}
                </p>
              )}
            </div>
            <div className="mt-8 flex space-x-3">
              <button
                onClick={() => reset()}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 dark:focus:ring-offset-gray-900 transition-colors">
                重试
              </button>
              <Link href="/" 
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-900 transition-colors">
                返回首页
              </Link>
              <button
                onClick={() => router.back()}
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-900 transition-colors">
                返回上一页
              </button>
            </div>
          </div>
        </main>
        
        <div className="mt-20 flex justify-center">
          <div className="relative w-full max-w-lg">
            <div className="absolute top-0 -left-4 w-72 h-72 bg-red-300 dark:bg-red-700 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
            <div className="absolute top-0 -right-4 w-72 h-72 bg-orange-300 dark:bg-orange-700 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
            <div className="absolute -bottom-8 left-20 w-72 h-72 bg-yellow-300 dark:bg-yellow-700 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
            <div className="relative">
              <div className="p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg dark:shadow-xl">
                <h3 className="text-lg font-medium text-gray-800 dark:text-gray-200 mb-2">需要帮助？</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">如果问题持续存在，您可以：</p>
                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li className="flex items-center">
                    <span className="mr-2 text-red-500">•</span> 
                    清除浏览器缓存并刷新页面
                  </li>
                  <li className="flex items-center">
                    <span className="mr-2 text-red-500">•</span>
                    稍后再试，服务器可能暂时过载
                  </li>
                  <li className="flex items-center">
                    <span className="mr-2 text-red-500">•</span>
                    联系我们的技术支持团队
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}